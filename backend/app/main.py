import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.authorization.roles.service import RoleService
from app.authorization.service import AuthorizationService
from app.core.auth.device_flows.background_tasks import cleanup_device_flow_table_task
from app.core.auth.jwt import oidc
from app.core.auth.router import router as auth
from app.core.authz.background_tasks import check_expired_admins
from app.core.errors.error_handling import add_exception_handlers
from app.core.logging import logger
from app.core.logging.scarf_analytics import backend_analytics
from app.core.webhooks.webhook import call_webhook
from app.data_output_configuration.registry import PluginRegistry
from app.database import database
from app.mcp.mcp import mcp
from app.mcp.middleware import LoggingMiddleware
from app.mcp.router import router as mcp_router
from app.settings import settings
from app.shared.router import router
from app.shared.schema import ORMModel

with open(Path(__file__).parent.parent / "VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal"

# Plugin discovery happens automatically in _build_runtime_union()
# when DataOutputConfiguration is first imported


# Log plugin initialization (discovery already happened during router import)
logger.info(f"Initialized {len(PluginRegistry.get_all())} plugins")

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
    # Auto-run migrations if enabled
    # Plugin discovery already happened at module import time
    if settings.AUTO_RUN_PLUGIN_MIGRATIONS:
        logger.info("Auto-running plugin migrations...")
        PluginRegistry.ensure_plugin_tables()

    db = next(database.get_db_session())
    resync = RoleService(db).initialize_prototype_roles()
    if resync or settings.AUTHORIZER_STARTUP_SYNC:
        AuthorizationService(db).reload_enforcer()

    backend_analytics(API_VERSION)
    admin_task = asyncio.create_task(check_expired_admins())
    device_flow_cleanup_task = asyncio.create_task(cleanup_device_flow_table_task())
    yield
    admin_task.cancel()
    device_flow_cleanup_task.cancel()


# Combine both lifespans
@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Run both lifespans
    async with lifespan(app), mcp_app.lifespan(app):
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
    swagger_ui_parameters={
        "docExpansion": "none",
        "tagsSorter": "alpha",
    },
)

mcp_app = mcp.http_app(path="/mcp")
mcp.add_middleware(LoggingMiddleware())

# Router registration moved to lifespan after plugin loading
# app.include_router(router, prefix="/api")  # Now in lifespan
app.include_router(auth, prefix="/api")
app.include_router(mcp_router)

add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
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


# K8S health and liveness check
@app.get("/", include_in_schema=False)
def root():
    return {"message": "Hello World"}


@app.get("/api/version", deprecated=True, tags=["Version"])
def get_version_old():
    return {"version": app.version}


class VersionResponse(ORMModel):
    version: str


@app.get("/api/v2/version", tags=["Version"])
def get_version():
    return VersionResponse(version=app.version)


# Note: use_route_names_as_operation_ids moved to lifespan
def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function names.
    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v2"):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)
