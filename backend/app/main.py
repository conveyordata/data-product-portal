import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.authorization.service import AuthorizationService
from app.core.auth.jwt import get_oidc, oidc
from app.core.auth.router import router as auth
from app.core.errors.error_handling import add_exception_handlers
from app.core.logging import logger
from app.core.logging.scarf_analytics import backend_analytics
from app.core.webhooks.webhook import call_webhook
from app.database import database
from app.mcp import LoggingMiddleware, mcp
from app.roles.service import RoleService
from app.settings import settings
from app.shared.router import router

with open(Path(__file__).parent.parent / "VERSION", "r") as f:
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
    db = next(database.get_db_session())
    resync = RoleService(db).initialize_prototype_roles()
    if resync or settings.AUTHORIZER_STARTUP_SYNC:
        AuthorizationService(db).reload_enforcer()

    backend_analytics(API_VERSION)
    yield


# Combine both lifespans
@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Run both lifespans
    async with lifespan(app):
        async with mcp_app.lifespan(app):
            yield


app = FastAPI(
    title=TITLE,
    summary="Backend API implementation for Data product portal",
    version=API_VERSION,
    contact={"name": "Stijn Janssens", "email": "stijn.janssens@dataminded.com"},
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=combined_lifespan,
    **oidc_kwargs,
)

mcp_app = mcp.http_app(path="/mcp")
mcp.add_middleware(LoggingMiddleware())

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
app.mount("/mcp", mcp_app)


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


@app.get("/.well-known/oauth-authorization-server")
def oauth_metadata() -> JSONResponse:
    """OAuth 2.1 Authorization Server Metadata."""
    return JSONResponse(
        {
            "issuer": get_oidc().authority,
            "authorization_endpoint": get_oidc().authorization_endpoint,
            "token_endpoint": get_oidc().token_endpoint,
            "jwks_uri": get_oidc().jwks_uri,
            "registration_endpoint": f"{settings.HOST}api/register",
            "response_types_supported": ["code"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["client_secret_post"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
        }
    )


# OpenID Connect Discovery endpoint
@app.get("/.well-known/openid-configuration")
async def openid_config():
    """OpenID Connect Discovery endpoint."""
    # In a real implementation, you might proxy to an actual OIDC provider
    return JSONResponse(
        {
            "issuer": get_oidc().authority,
            "authorization_endpoint": get_oidc().authorization_endpoint,
            "token_endpoint": get_oidc().token_endpoint,
            "jwks_uri": get_oidc().jwks_uri,
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
    )


# OAuth Protected Resource Metadata
@app.get("/.well-known/oauth-protected-resource")
def oauth_protected_resource():
    """OAuth 2.1 Protected Resource Metadata."""
    BASE_URL = settings.HOST
    return JSONResponse(
        {
            "resource": BASE_URL,
            "authorization_servers": [BASE_URL],
            "jwks_uri": get_oidc().jwks_uri,
            "bearer_methods_supported": ["header"],
            "resource_documentation": f"{BASE_URL}/docs",
        }
    )


# Dynamic Client Registration endpoint
@app.post("/api/register")
async def register(request: Request):
    """OAuth 2.1 Dynamic Client Registration endpoint."""
    logger.info(f"/register headers: {dict(request.headers)}")
    raw_body = await request.body()
    logger.info(f"/register raw body: {raw_body}")

    try:
        data = await request.json()
        print(data)
        logger.info(f"/register parsed data: {data}")
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {e}")
        return JSONResponse(
            {"error": "Invalid JSON body", "details": str(e)}, status_code=400
        )

    # Generate client credentials
    client_id = get_oidc().client_id
    client_secret = get_oidc().client_secret
    now = int(time.time())

    # Build the response according to OAuth 2.0 Dynamic Client Registration spec
    response_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_id_issued_at": now,
        "client_secret_expires_at": 0,  # 0 means no expiration
        "redirect_uris": ["http://localhost:5050/"],  # data.get("redirect_uris", []),
        "token_endpoint_auth_method": data.get(
            "token_endpoint_auth_method", "client_secret_post"
        ),
        "grant_types": data.get("grant_types", ["authorization_code"]),
        "response_types": data.get("response_types", ["code"]),
        "client_name": data.get("client_name", ""),
        "scope": data.get("scope", ""),
    }

    logger.info(f"/register response: {response_data}")
    return JSONResponse(response_data, status_code=201)


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
