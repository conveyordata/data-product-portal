import asyncio
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastmcp.utilities.lifespan import combine_lifespans
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.authorization.service import AuthorizationService
from app.core.auth.device_flows.background_tasks import cleanup_device_flow_table_task
from app.core.auth.jwt import get_oidc
from app.core.auth.router import router as auth
from app.core.authz.background_tasks import check_expired_admins
from app.core.context import _pending_events, pop_events
from app.core.errors.error_handling import add_exception_handlers
from app.core.logging import logger
from app.core.logging.scarf_analytics import backend_analytics
from app.core.webhooks.v2 import call_v2_webhook
from app.core.webhooks.webhook import call_webhook, register_webhooks
from app.database import database
from app.mcp.mcp import mcp
from app.mcp.middleware import LoggingMiddleware
from app.settings import settings
from app.shared.router import router
from app.shared.schema import ORMModel

with open(Path(__file__).parent.parent / "VERSION", "r") as f:
    API_VERSION = f.read().strip()

TITLE = "Data product portal"

oidc_kwargs = (
    {
        "swagger_ui_init_oauth": {
            "clientId": get_oidc().client_id,
            "appName": TITLE,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid email profile",
        },
        "swagger_ui_oauth2_redirect_url": "/api/oauth2-redirect",
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
    with database.SessionLocal() as db:
        if settings.AUTHORIZER_STARTUP_SYNC:
            AuthorizationService(db).reload_enforcer()
        db.commit()

    backend_analytics(API_VERSION)
    admin_task = asyncio.create_task(check_expired_admins())
    device_flow_cleanup_task = asyncio.create_task(cleanup_device_flow_table_task())
    yield
    admin_task.cancel()
    device_flow_cleanup_task.cancel()


mcp.add_middleware(LoggingMiddleware())
mcp_app = mcp.http_app("/")

app = FastAPI(
    title=TITLE,
    summary="Backend API implementation for Data product portal",
    version=API_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=combine_lifespans(lifespan, mcp_app.lifespan),
    **oidc_kwargs,
    swagger_ui_parameters={
        "docExpansion": "none",
        "tagsSorter": "alpha",
    },
)

app.mount("/mcp", mcp_app)
# We need to add the MCP well known authentication routes here.
# The problem is we mounted the MCP under `/mcp`, but these need to be mounted without that.
# So we add the well_known routes properly
if mcp_auth := mcp.auth:
    for route in mcp_auth.get_well_known_routes("/"):
        logger.debug(f"Adding route {route.path} for MCP authentication")
        app.add_route(
            route.path, route.endpoint, methods=route.methods, include_in_schema=False
        )

app.include_router(router, prefix="/api")
app.include_router(auth, prefix="/api")

add_exception_handlers(app)
register_webhooks(app)

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
async def send_response_to_webhook(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    # Gets are not logged
    if (
        settings.WEBHOOK_URL
        and request.method in ["POST", "PUT", "DELETE"]
        and not (
            request.url.path.startswith("/api/auth/")
            or request.url.path.startswith("/api/v2/authn/")
        )
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


@app.middleware("http")
async def dispatch_queued_events(request: Request, call_next):
    token = _pending_events.set([])
    try:
        response = await call_next(request)
    finally:
        events = pop_events()
        _pending_events.reset(token)
    if response.status_code < 400 and settings.WEBHOOK_V2_URL:
        for event in events:
            asyncio.create_task(
                call_v2_webhook(type(event).event_type(), event.model_dump(mode="json"))
            )
    return response


class VersionResponse(ORMModel):
    version: str


@app.get("/api/v2/version", tags=["Version"])
def get_version():
    return VersionResponse(version=app.version)


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function names.
    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v2"):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)


class SPAStaticFiles(StaticFiles):
    """StaticFiles subclass that falls back to index.html for unknown paths.
    Which is required for SPAs (single page applications).
    """

    async def get_response(self, path: str, scope):  # type: ignore[override]
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


if settings.SERVE_FRONTEND:
    _frontend_dir = Path(settings.FRONTEND_DIST_DIR)
    if _frontend_dir.exists():
        app.mount(
            "/",
            SPAStaticFiles(directory=str(_frontend_dir), html=True),
            name="frontend",
        )
    else:
        raise Exception("Frontend dist directory not found")

if settings.OPENTELEMETRY_TRACES_ENABLED:
    logger.info(
        f"Tracing enabled setting it up with service name: ${settings.OPENTELEMETRY_TRACES_SERVICE_NAME}"
    )
    # Import inside to avoid loading OTEL modules when tracing is disabled
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {"service.name": settings.OPENTELEMETRY_TRACES_SERVICE_NAME}
    )
    provider = TracerProvider(resource=resource)

    logger.info(
        f"Setting up tracing with endpoint: {settings.OPENTELEMETRY_TRACES_ENDPOINT} insecure: {settings.OPENTELEMETRY_TRACES_ENDPOINT_INSECURE}"
    )
    exporter = OTLPSpanExporter(
        endpoint=settings.OPENTELEMETRY_TRACES_ENDPOINT,
        insecure=settings.OPENTELEMETRY_TRACES_ENDPOINT_INSECURE,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
