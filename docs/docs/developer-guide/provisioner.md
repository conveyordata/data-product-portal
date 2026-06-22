# How to use the provisioner SDK

The Data Product Portal SDK includes a Kubernetes-operator-style **reconcile loop** that
lets you build provisioners — services that react to portal events and converge real
infrastructure (S3 buckets, database schemas, Terraform workspaces, …) towards the
desired state declared in the portal.

This guide walks you through the core concepts, then shows you how to build and run your
own provisioner using the bundled example as a reference.

---

## How it works

When a resource (exploration, data product, output port, …) is created, updated, or
deleted in the portal, the portal fires a **CloudEvent** webhook. The reconcile manager
receives the event and triggers the reconcile of your provisioner. Your provisioner needs
to implement the reconcile method in general so that it follows this pattern:
- Fetch current state from portal and infrastructure
- Compare the portal state and infrastructure state with desired state
- Make changes to infrastructure and/or portal to match desired state

This **resource based reconciler** approach has a couple of important properties:

- **Idempotent** — rerunning a reconcile should always produce the same outcome for the same portal state
- **Coalescing** — multiple rapid events for the same resource (e.g. several quick
  edits) collapse into a single reconcile, preventing redundant infrastructure calls.
- **Single Execution Per Resource** — a given resource ID is **never reconciled by two workers at the same time**, regardless
  of how many workers you run.
- **Concurrency**: Multiple workers can run concurrently

```
portal ──(webhook event)──▶ POST /webhook ──▶ ReconcileEventHandler
                                                      │
                                              enqueues resource id
                                                      │
                                              ReconcileManager (workers)
                                                      │
                                          Your Reconciler.reconcile()
                                                      │
                                     compare current vs desired state and make updates
```

---

## Key SDK components

### `Reconciler`

The abstract base class you implement. It exposes two methods:

| Method                    | Purpose                                                                                                                                        |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `reconcile(resource_id)`  | Called for each resource that needs to be reconciled. Raise an exception to signal failure; the framework will retry with exponential backoff. |
| `list_ids()` *(optional)* | Called once on startup, you should return all the existing ID's of resources in Portal for which you want to call the `reconcile(resource_id)`. |

We currently support 2 resources:
- Data Product: Your reconcile function will be triggered on changes to the Data Product itself, its Output Ports, Technical Assets, Technical Asset Output Port links, Input Ports, Role Assignments etc.
- Exploration: Your reconcile function will be triggered on changes to the Exploration itself, and its Input Ports.

### `ReconcileManager`

Drives one or more `Reconciler` instances from a shared, deduplicated work queue. Key
constructor parameters:

| Parameter       | Default | Description                                                                                                                              |
|-----------------|---------|------------------------------------------------------------------------------------------------------------------------------------------|
| `reconcilers`   | `{}`    | Mapping of `ResourceType` → `Reconciler`                                                                                                 |
| `default_delay` | `5.0 s` | Debounce — how long after an event to wait before picking the resource up, in the mean time we will compact events for the same resource |
| `num_workers`   | `1`     | Number of concurrent worker tasks                                                                                                        |

A given resource ID is **never reconciled by two workers at the same time**, regardless
of how many workers you run.

### `ReconcileEventHandler`

A FastAPI-ready webhook handler. Pass it a `ReconcileManager` and call
`handler.dispatch_routing(request)` from your `/webhook` endpoint. It parses the
incoming CloudEvent, maps it to the right `ResourceType`, and enqueues a reconcile.
Events for resource types that have no registered reconciler are silently acknowledged.

### `ResourceType`

An enum of the portal resource types your provisioner can react to:

- `ResourceType.EXPLORATION`
- `ResourceType.DATA_PRODUCT`

---

## Building your own provisioner

### 1. Set up your project

Create a `pyproject.toml` for your provisioner and add the SDK as a dependency:

```toml
[tool.poetry]
name = "my-provisioner"
version = "0.1.0"
description = ""

[tool.poetry.dependencies]
python = ">=3.13"
data-product-portal-sdk = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Then install:

```bash
poetry install
```

### 2. Implement a `Reconciler`

Subclass `Reconciler` and implement `reconcile`. The full example below manages an
exploration with finalizers and a startup resync; the same pattern applies to
`DATA_PRODUCT`.

```python
from collections.abc import Iterable
from uuid import UUID

from sdk import AuthenticatedClient, Client, Reconciler
from sdk.api_client.api.explorations import (
    add_exploration_finalizer,
    get_exploration,
    get_explorations,
    remove_exploration_finalizer,
)
from sdk.api_client.models import GetExplorationResponse, GetExplorationsResponse
from sdk.api_client.models.abstract_data_product_status import AbstractDataProductStatus
from sdk.api_client.models.finalizer_request import FinalizerRequest

FINALIZER_NAME = "my-provisioner"  # must be unique across all provisioners


class MyExplorationProvisioner(Reconciler):
    def __init__(self, client: Client | AuthenticatedClient) -> None:
        self._client = client

    async def reconcile(self, resource_id: UUID) -> None:
        response = await get_exploration.asyncio(id=resource_id, client=self._client)

        if response is None:
            # Hard-deleted after we already removed our finalizer — nothing to do.
            return

        if not isinstance(response, GetExplorationResponse):
            raise Exception(f"Unexpected response: {response}")

        if response.status == AbstractDataProductStatus.DELETING:
            # Portal is waiting for us to clean up before hard-deleting.
            if FINALIZER_NAME not in (response.finalizers or []):
                return  # another reconcile already deprovisioned
            self._deprovision(resource_id)
            await remove_exploration_finalizer.asyncio(
                id=resource_id, finalizer=FINALIZER_NAME, client=self._client
            )
            return

        # Exploration is live (ACTIVE / PENDING / ARCHIVED).
        # Register the finalizer *before* provisioning so even a partial
        # provision is cleaned up when the exploration is later deleted.
        await add_exploration_finalizer.asyncio(
            id=resource_id,
            client=self._client,
            body=FinalizerRequest(finalizer=FINALIZER_NAME),
        )
        self._provision(resource_id, response)

    async def list_ids(self) -> Iterable[UUID]:
        response = await get_explorations.asyncio(client=self._client)
        if isinstance(response, GetExplorationsResponse):
            return [e.id for e in response.explorations]
        return []

    def _provision(self, resource_id: UUID, exploration: GetExplorationResponse) -> None:
        # Create or update your real infrastructure here.
        ...

    def _deprovision(self, resource_id: UUID) -> None:
        # Tear down the infrastructure here.
        ...
```

#### 2.1 Resource-based reconciliation

`reconcile` is called with only the resource ID. It must re-fetch the current desired
state from the portal itself and converge infrastructure towards it. This makes
reconciliation **idempotent**: running it twice produces the same result, and coalesced
events (e.g. three rapid updates) result in a single infrastructure call.

If `reconcile` raises an exception the framework automatically retries it with
exponential backoff, so transient API failures or flaky infrastructure are handled
for you without any extra code.

#### 2.2 Finalizers

[Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/) let your provisioner block the portal from hard-deleting a resource until
your clean-up is complete. The pattern is:

1. **Before provisioning** — call `add_exploration_finalizer` to register your name.
   This ensures that even if a partial provision fails halfway, the deletion path will
   still run `_deprovision`.
2. **On `DELETING` status** — run `_deprovision`, then call
   `remove_exploration_finalizer`. The portal only performs the hard-delete once all
   registered finalizers have been removed.
3. **Guard against double-deprovision** — check that your finalizer name is still
   present in `response.finalizers` before acting; a previous reconcile run may have
   already cleaned up.

#### 2.3 Startup resync

`list_ids` is called once when the `ReconcileManager` starts. Return every resource ID
your provisioner is responsible for so that the full set is reconciled before any
webhook event arrives. This catches resources that were created or changed while the
provisioner was offline.
It also helps you to manage updates to your provisioner code, when you update the provisioner to generate extra infra
by default, or you correct certain bugs in your provisioner, you can ensure that your provisioner is reconciled for every
resource it manages.

### 3. Wire everything into a FastAPI app

```python
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request
from sdk import PortalAuth, ReconcileEventHandler, ReconcileManager, ResourceType

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = PortalAuth().get_client()
    manager = ReconcileManager(
        {ResourceType.EXPLORATION: MyExplorationProvisioner(client)},
        default_delay=30.0,  # debounce in seconds, can be lowered for faster reconciles, however setting it too low is not recommended. It depends how "cheap" your reconcile is.
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
```

---

## Running the provisioner

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PORTAL_BASE_URL` | Yes | Base URL of the portal API, e.g. `http://localhost:5050` |
| `PORTAL_*` auth vars | Depends | See the SDK README for authentication options |

### Start the server

```bash
PORTAL_BASE_URL="http://localhost:5050" \
  poetry run uvicorn my_provisioner:app --reload
```

Then configure the portal's webhook URL to point at your running provisioner:

```
http://localhost:8000/webhook
```

---

## Running the bundled example

The `sdk/example/` directory contains a complete, runnable provisioner that writes
per-exploration JSON manifests to disk (a stand-in for real infrastructure).

```bash
cd sdk
poetry install --all-groups

PORTAL_BASE_URL="http://localhost:5050" \
PROVISIONER_WORKSPACE="./.workspace" \
  poetry run uvicorn example.provisioner:app --reload
```

Create, update, or delete an exploration in the portal and watch manifests appear and
disappear under `.workspace/`. Use this as a starting point for your own provisioner.

---


## FAQ

### How should I handle Input Port and Technical Asset changes?

When an Input Port is created or approved, the SDK enqueues a reconcile for the
**consuming** Data Product (or Exploration). When a Technical Asset is added to or
removed from an Output Port, the SDK enqueues a reconcile for the **owning Data
Product**.

We generally recommend the following pattern:

- **Output Port created / updated** — provision a role (e.g. an IAM policy, a Postgres
  role, a Snowflake role) that grants access to the underlying assets encapsulated in the Output Port.
- **Input Port created / approved** — assign that role to the consumer's principal.
- **Input Port removed / rejected** — revoke the role assignment from the consumer's
  principal.
