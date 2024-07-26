import time

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth.jwt import oidc
from app.core.auth.router import router as auth
from app.core.errors.error_handling import ErrorHandler
from app.core.logging.logger import setup_logger
from app.settings import settings
from app.shared.router import router

with open("./VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal"

oidc_kwargs = (
    {}
    if settings.OIDC_DISABLED
    else {
        "swagger_ui_init_oauth": {
            "clientId": oidc.client_id,
            "appName": TITLE,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid email profile",
        },
        "swagger_ui_oauth2_redirect_url": "/",
    }
)
app = FastAPI(
    title=TITLE,
    summary=(
        "Backend API implementation for Data product portal, "
        "your enterprise-ready data access tool"
    ),
    version=API_VERSION,
    contact={"name": "Stijn Janssens", "email": "stijn.janssens@dataminded.com"},
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    **oidc_kwargs
)

app.include_router(router, prefix="/api")
app.include_router(auth, prefix="/api")

logger = setup_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return ErrorHandler().raise_exception(exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return ErrorHandler().raise_validation_exception(exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return ErrorHandler().raise_generic_exception(request, exc)


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


app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)


# K8S health and liveness check
@app.get("/")
def root():
    return {"message": "Hello World"}
