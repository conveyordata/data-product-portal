import asyncio
import re
import urllib.parse
from collections.abc import Coroutine
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRoute
from fastmcp.utilities.lifespan import combine_lifespans

from app.abstract_data_product.background_tasks import check_stuck_deletions
from app.abstract_data_product.input_ports.background_tasks import (
    expire_input_ports_task,
)
from app.authorization.service import AuthorizationService
from app.core.auth.device_flows.background_tasks import cleanup_device_flow_table_task
from app.core.auth.jwt import get_oidc
from app.core.auth.router import router as auth
from app.core.authz.background_tasks import check_expired_admins
from app.core.errors.error_handling import add_exception_handlers
from app.core.logging import logger
from app.core.logging.middleware import RequestLoggingMiddleware
from app.core.logging.posthog_analytics import report_daily_metrics
from app.core.logging.scarf_analytics import backend_analytics
from app.core.webhooks.middleware import (
    DispatchQueuedEventsMiddleware,
    start_event_dispatcher,
    stop_event_dispatcher,
)
from app.core.webhooks.webhook import register_webhooks
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


def _log_background_task_result(task: asyncio.Task[None]) -> None:
    if task.cancelled():
        return
    if exc := task.exception():
        logger.exception(
            "Background task '%s' failed",
            task.get_name(),
            exc_info=exc,
        )


def _create_supervised_task(
    coro: Coroutine[Any, Any, None], *, name: str
) -> asyncio.Task[None]:
    task: asyncio.Task[None] = asyncio.create_task(coro, name=name)
    task.add_done_callback(_log_background_task_result)
    return task


async def _cancel_tasks(tasks: list[asyncio.Task[None]]) -> None:
    for task in tasks:
        task.cancel()
    for task in tasks:
        with suppress(asyncio.CancelledError):
            await task


@asynccontextmanager
async def lifespan(app: FastAPI):
    with database.SessionLocal() as db:
        if settings.AUTHORIZER_STARTUP_SYNC:
            AuthorizationService(db).reload_enforcer()
        db.commit()

    backend_analytics(API_VERSION)
    background_tasks = [
        _create_supervised_task(check_expired_admins(), name="check_expired_admins"),
        _create_supervised_task(
            cleanup_device_flow_table_task(),
            name="cleanup_device_flow_table_task",
        ),
        _create_supervised_task(
            report_daily_metrics(),
            name="report_north_star_metrics",
        ),
        _create_supervised_task(check_stuck_deletions(), name="check_stuck_deletions"),
        _create_supervised_task(
            expire_input_ports_task(),
            name="expire_input_ports_task",
        ),
    ]
    start_event_dispatcher(app)
    yield
    await _cancel_tasks(background_tasks)
    await stop_event_dispatcher(app)


mcp.add_middleware(LoggingMiddleware())
_mcp_host = settings.MCP_BASE_URL or settings.HOST
_mcp_allowed_hosts = [urllib.parse.urlparse(_mcp_host).hostname] if _mcp_host else []
mcp_app = mcp.http_app(
    "/",
    allowed_hosts=_mcp_allowed_hosts or None,
    stateless_http=settings.MCP_STATELESS_HTTP,
)


def route_as_operation_id(route: APIRoute) -> str:
    return re.sub(r"\W", "_", route.name.lower())


app = FastAPI(
    title=TITLE,
    summary="Backend API implementation for Data product portal",
    version=API_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=combine_lifespans(lifespan, mcp_app.lifespan),
    generate_unique_id_function=route_as_operation_id,
    swagger_ui_parameters={
        "docExpansion": "none",
        "tagsSorter": "alpha",
    },
    **oidc_kwargs,
)

app.mount("/mcp", mcp_app)


@app.api_route(
    "/mcp",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def redirect_mcp_to_slash(request: Request):
    return RedirectResponse(url="/mcp/", status_code=307)


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

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(DispatchQueuedEventsMiddleware, fastapi_app=app)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VersionResponse(ORMModel):
    version: str


@app.get("/api/v2/version", tags=["Version"])
def get_version():
    return VersionResponse(version=app.version)


if settings.SERVE_FRONTEND:
    app.frontend("/", directory=Path(settings.FRONTEND_DIST_DIR), fallback="index.html")

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
