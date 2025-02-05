import asyncio
import time
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.authz.authorization import Authorization
from app.core.auth.jwt import oidc
from app.core.auth.router import router as auth
from app.core.errors.error_handling import add_exception_handlers
from app.core.logging.logger import logger
from app.core.logging.scarf_analytics import backend_analytics
from app.core.webhooks.webhook import call_webhook
from app.settings import settings
from app.shared.router import router

with open("./VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal"

oidc_kwargs = (
    {
        "swagger_ui_init_oauth": {
            "clientId": oidc.client_id,
            "appName": TITLE,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid email profile",
        },
        "swagger_ui_oauth2_redirect_url": "/",
    }
    if settings.OIDC_ENABLED
    else {}
)


async def log_middleware(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start
    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "status": response.status_code,
        "process_time": process_time,
    }
    if request.url.path != "/":  # ignore health checks on root path
        logger.info(log_dict)
    return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    await Authorization.initialize()
    yield


backend_analytics()
app = FastAPI(
    title=TITLE,
    summary="Backend API implementation for Data product portal",
    version=API_VERSION,
    contact={"name": "Stijn Janssens", "email": "stijn.janssens@dataminded.com"},
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    **oidc_kwargs
)

app.include_router(router, prefix="/api")
app.include_router(auth, prefix="/api")

add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
)


@app.middleware("http")
async def send_response_to_webhook(request: Request, call_next):
    response = await call_next(request)
    # Gets are not logged
    if (
        settings.WEBHOOK_URL
        and request.method in ["POST", "PUT", "DELETE"]
        and not request.url.path.startswith("/api/auth/")
    ):
        body = ""
        if request.method == "POST":
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            body = (b"".join(response_body)).decode()
        asyncio.create_task(
            call_webhook(
                content=body,
                method=request.method,
                url=request.url.path,
                query=request.url.query,
                status_code=response.status_code,
            )
        )
    return response


# K8S health and liveness check
@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/version")
def get_version():
    return {"version": app.version}


@app.webhooks.post("generic")
def new_data_product():
    """
    Whenever something changes in the Portal state,
    this webhook will be triggered.
    All POST, PUT and DELETE calls are forwarded
    """
