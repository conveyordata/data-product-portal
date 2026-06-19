import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from provisioner.reconciler import DataProductReconciler
from sdk import (
    PortalAuth,
    ReconcileEventHandler,
    ReconcileManager,
    ResourceType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


client = PortalAuth().get_client()

manager = ReconcileManager({ResourceType.DATA_PRODUCT: DataProductReconciler(client)})
event_handler = ReconcileEventHandler(manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting reconcile manager")
    manager.start()
    try:
        yield
    finally:
        logging.info("Stopping reconcile manager")
        await manager.stop()


app = FastAPI(title="Provisioner Webhook Handler", lifespan=lifespan)


@app.get("/")
def get_root(request: Request):
    """Basic root endpoint for health checks."""
    logging.debug(
        f"GET request from {request.client.host if request.client else 'unknown'}"
    )
    return {"status": "ok"}


@app.post("/")
async def post_root(request: Request):
    """Main webhook entrypoint. Parses the CloudEvent and enqueues a reconcile."""
    logging.info(
        f"Received POST request from {request.client.host if request.client else 'unknown'}"
    )
    return await event_handler.dispatch_routing(request)
