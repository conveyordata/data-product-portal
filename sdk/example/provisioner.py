"""A worked example provisioner built on the SDK reconcile loop.

This shows how to turn portal webhook events into an operator-style control loop.
:class:`ExplorationProvisioner` and :class:`DomainProvisioner` are implementations
of such a reconciler.
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
from http import HTTPStatus
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
from sdk.api_client.api.configuration_domains import (
    add_domain_finalizer,
    get_domain,
    get_domains,
    remove_domain_finalizer,
)
from sdk.api_client.api.explorations import (
    add_exploration_finalizer,
    get_exploration,
    get_explorations,
    remove_exploration_finalizer,
)
from sdk.api_client.models import (
    DomainStatus,
    GetDomainResponse,
    GetDomainsResponse,
    GetExplorationResponse,
    GetExplorationsResponse,
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

# Identifier this provisioner registers on every exploration and domain it manages.
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

        fetched = await get_exploration.asyncio_detailed(
            id=exploration_id, client=self._client
        )
        if fetched.status_code == HTTPStatus.NOT_FOUND:
            # Exploration is fully gone from the portal. Because we always register
            # our finalizer before provisioning, the portal will only hard-delete
            # after we have already deprovisioned via the DELETING path. Nothing to do.
            return
        if not isinstance(fetched.parsed, GetExplorationResponse):
            # Any other failure (401, 500, ...) must be retried, not treated as deleted.
            raise Exception(f"Could not fetch exploration: {fetched.status_code}")
        response = fetched.parsed

        if response.status == AbstractDataProductStatus.DELETING:
            # Portal is waiting for us to finish clean-up before hard-deleting.
            # Only act if we are still registered — another reconcile may have
            # already deprovisioned and released our finalizer.
            if FINALIZER_NAME not in (response.finalizers or []):
                return
            self._deprovision(exploration_id)
            removed = await remove_exploration_finalizer.asyncio_detailed(
                id=exploration_id,
                finalizer=FINALIZER_NAME,
                client=self._client,
            )
            if removed.status_code != HTTPStatus.OK:
                raise Exception(f"Could not remove finalizer: {removed.status_code}")
            return

        # Exploration is live (ACTIVE / PENDING / ARCHIVED).
        # Register the finalizer *before* provisioning so that even a partial
        # provision is cleaned up when the exploration is later deleted.
        added = await add_exploration_finalizer.asyncio_detailed(
            id=exploration_id,
            client=self._client,
            body=FinalizerRequest(finalizer=FINALIZER_NAME),
        )
        if added.status_code != HTTPStatus.OK:
            raise Exception(f"Could not add finalizer: {added.status_code}")
        self._provision(exploration_id, response)

    async def list_ids(self) -> Iterable[UUID]:
        """List every exploration in the portal so each is reconciled on startup."""
        response = await get_explorations.asyncio(client=self._client)
        if isinstance(response, GetExplorationsResponse):
            return [exploration.id for exploration in response.explorations]
        # Raise so the startup sync retries instead of reconciling nothing.
        raise Exception("Could not list explorations")

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


class DomainProvisioner(Reconciler):
    """Provisions a per-domain workspace directory + manifest.

    Stands in for domain-scoped infrastructure shared by every data product in the
    domain (a bucket, a VPC, a catalog, ...). Name such resources after the domain
    ``namespace``, which never changes, rather than its editable ``name``.
    """

    def __init__(
        self, client: Client | AuthenticatedClient, workspace: Path = WORKSPACE
    ) -> None:
        self._client = client
        self._workspace = workspace / "domains"

    def _path_for(self, namespace: str) -> Path:
        return self._workspace / namespace / "manifest.json"

    async def reconcile(self, domain_id: UUID):
        logger.info("Reconciling domain %s", domain_id)

        fetched = await get_domain.asyncio_detailed(id=domain_id, client=self._client)
        if fetched.status_code == HTTPStatus.NOT_FOUND:
            return
        if not isinstance(fetched.parsed, GetDomainResponse):
            raise Exception(f"Could not fetch domain: {fetched.status_code}")
        response = fetched.parsed

        if response.status == DomainStatus.DELETING:
            if FINALIZER_NAME not in response.finalizers:
                return
            self._deprovision(response.namespace)
            removed = await remove_domain_finalizer.asyncio_detailed(
                id=domain_id, finalizer=FINALIZER_NAME, client=self._client
            )
            if removed.status_code != HTTPStatus.OK:
                raise Exception(f"Could not remove finalizer: {removed.status_code}")
            return

        # Never provision without our finalizer, or the deletion would skip cleanup.
        added = await add_domain_finalizer.asyncio_detailed(
            id=domain_id,
            client=self._client,
            body=FinalizerRequest(finalizer=FINALIZER_NAME),
        )
        if added.status_code != HTTPStatus.OK:
            raise Exception(f"Could not add finalizer: {added.status_code}")
        self._provision(response)

    async def list_ids(self) -> Iterable[UUID]:
        response = await get_domains.asyncio(client=self._client)
        if isinstance(response, GetDomainsResponse):
            return [domain.id for domain in response.domains]
        raise Exception("Could not list domains")

    def _provision(self, domain: GetDomainResponse):
        manifest = {
            "id": str(domain.id),
            "name": domain.name,
            "namespace": domain.namespace,
        }
        path = self._path_for(domain.namespace)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2))
        logger.info("Provisioned domain %s at %s", domain.namespace, path)

    def _deprovision(self, namespace: str):
        path = self._path_for(namespace)
        if not path.exists():
            logger.info("Domain %s already absent, nothing to deprovision", namespace)
            return
        path.unlink()
        try:
            path.parent.rmdir()
        except OSError:
            pass
        logger.info("Deprovisioned domain %s", namespace)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = _build_client()
    manager = ReconcileManager(
        {
            ResourceType.EXPLORATION: ExplorationProvisioner(client),
            ResourceType.DOMAIN: DomainProvisioner(client),
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
