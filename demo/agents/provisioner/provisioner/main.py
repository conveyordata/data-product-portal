from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request

from .reconciler import DataProductReconciler
from sdk import PortalAuth
from sdk.provisioner.reconcile_manager import (
    ReconcileManager,
    ResourceType,
    ReconcileEventHandler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Reads auth setups from corresponding PORTAL_* environment variables automatically
    client = PortalAuth().get_client()

    manager = ReconcileManager(
        reconcilers={ResourceType.DATA_PRODUCT: DataProductReconciler(client)},
        default_delay=5.0,
        num_workers=4,
    )

    manager.start()
    app.state.manager = manager
    app.state.handler = ReconcileEventHandler(manager)

    try:
        yield
    finally:
        await manager.stop()
        await client.get_async_httpx_client().aclose()


app = FastAPI(title="Data Product Reconciler Provisioner", lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, Any]:
    """Single ingress webhook receiving structural CloudEvents via SDK parsing."""
    await request.app.state.handler.dispatch_routing(request)
    return {"status": "accepted", "detail": "Event enqueued for reconciliation"}


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
