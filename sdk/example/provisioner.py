"""A worked example provisioner built on the SDK reconcile loop.

This shows how to turn portal webhook events into an operator-style control loop.
The :class:`ExplorationProvisioner` is an implementation of such a reconciler.
On every event it (re-)fetches the current state of the
resource from the portal and converge an external resource towards it. Here the
"external resource" is a directory on disk containing a small manifest, which stands
in for whatever real infrastructure a provisioner would manage (an S3 prefix, a
database schema, a Terraform workspace, ...).

Run it with::

    cd sdk
    poetry install --all-groups
    poetry run uvicorn example.provisioner:app --reload

and point the portal's webhook at ``http://localhost:8000/webhook``.

Set ``PORTAL_BASE_URL`` (and the other ``PORTAL_*`` auth variables, see the README) so
the provisioner can call back into the portal. Set ``PROVISIONER_WORKSPACE`` to control
where manifests are written (defaults to ``./.workspace``).
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request

from sdk import (
    AuthenticatedClient,
    Client,
    PortalAuth,
    ReconcileEventHandler,
    ReconcileManager,
    Reconciler,
    ResourceType,
)
from sdk.api_client.api.explorations import (
    add_exploration_finalizer,
    get_exploration,
    get_explorations,
    remove_exploration_finalizer,
)
from sdk.api_client.models import (
    GetExplorationResponse,
    GetExplorationsResponse,
    HTTPValidationError,
)
from sdk.api_client.models.abstract_data_product_status import AbstractDataProductStatus
from sdk.api_client.models.finalizer_request import FinalizerRequest

_LOG_FORMAT = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
logger = logging.getLogger("example.provisioner")
_formatter = logging.Formatter(_LOG_FORMAT)
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    for _handler in logging.getLogger(_name).handlers:
        _handler.setFormatter(_formatter)

WORKSPACE = Path(os.getenv("PROVISIONER_WORKSPACE", ".workspace"))

# Identifier this provisioner registers on every exploration it manages.
# Must be unique across all provisioners that use finalizers.
FINALIZER_NAME = "example-provisioner"


def _build_client() -> Client | AuthenticatedClient:
    return PortalAuth().get_client()


class ExplorationProvisioner(Reconciler):
    """Provisions a per-exploration workspace directory + manifest.

    The reconcile is idempotent and level-based:

    - If the exploration still exists in the portal, (re-)write its manifest.
    - If the portal returns nothing (deleted / 404), remove the workspace.

    Because it always reads the *current* state, coalesced create/update/delete events
    converge to the right outcome regardless of how many fired or in which order.
    """

    def __init__(
        self, client: Client | AuthenticatedClient, workspace: Path = WORKSPACE
    ) -> None:
        self._client = client
        self._workspace = workspace

    def _path_for(self, exploration_id: UUID) -> Path:
        return self._workspace / str(exploration_id) / "manifest.json"

    async def reconcile(self, exploration_id: UUID):
        logger.info("Reconciling exploration %s", exploration_id)

        response = await get_exploration.asyncio(id=exploration_id, client=self._client)
        if response is None:
            # Exploration is fully gone from the portal — clean up locally.
            return
        if isinstance(response, HTTPValidationError):
            raise Exception(response.detail)
        if not isinstance(response, GetExplorationResponse):
            raise Exception("Unexpected response")

        if response.status == AbstractDataProductStatus.DELETING:
            # Portal is waiting for us to finish clean-up before hard-deleting.
            # Only act if we are still registered — another reconcile may have
            # already deprovisioned and released our finalizer.
            if FINALIZER_NAME not in (response.finalizers or []):
                return
            self._deprovision(exploration_id)
            await remove_exploration_finalizer.asyncio(
                id=exploration_id,
                finalizer=FINALIZER_NAME,
                client=self._client,
            )
            return

        # Exploration is live (ACTIVE / PENDING / ARCHIVED).
        # Register the finalizer *before* provisioning so that even a partial
        # provision is cleaned up when the exploration is later deleted.
        await add_exploration_finalizer.asyncio(
            id=exploration_id,
            client=self._client,
            body=FinalizerRequest(finalizer=FINALIZER_NAME),
        )
        self._provision(exploration_id, response)

    async def list_ids(self) -> Iterable[UUID]:
        """List every exploration in the portal so each is reconciled on startup."""
        response = await get_explorations.asyncio(client=self._client)
        if response is None:
            return []
        if isinstance(response, GetExplorationsResponse):
            return [exploration.id for exploration in response.explorations]
        if isinstance(response, HTTPValidationError):
            raise Exception(response.detail)
        raise Exception("Unexpected response")

    def _provision(self, exploration_id: UUID, exploration: GetExplorationResponse):
        manifest = {
            "id": str(exploration.id),
            "name": exploration.name,
            "namespace": exploration.namespace,
            "description": exploration.description,
            "domain": getattr(exploration.domain, "name", None),
            "owner": getattr(exploration.owner, "email", None),
        }
        path = self._path_for(exploration_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2))
        logger.info("Provisioned exploration %s at %s", exploration_id, path)

    def _deprovision(self, exploration_id: UUID):
        path = self._path_for(exploration_id)
        if path.exists():
            path.unlink()
            try:
                path.parent.rmdir()
            except OSError:
                pass
            logger.info("Deprovisioned exploration %s", exploration_id)
        else:
            logger.info(
                "Exploration %s already absent, nothing to deprovision", exploration_id
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = _build_client()
    manager = ReconcileManager(
        {
            ResourceType.EXPLORATION: ExplorationProvisioner(client),
        },
        default_delay=30.0,  # debounce: wait 30s before picking a resource up
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


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, Any]:
    return await request.app.state.handler.dispatch_routing(request)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
