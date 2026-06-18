# dpp-sdk

Python SDK for building [Data Product Portal](https://github.com/dataminded/data-product-portal) provisioners.

## Prerequisites

- Python ≥ 3.12
- [Poetry](https://python-poetry.org/) ≥ 2.0
- [Task](https://taskfile.dev/) (optional)

## Setup

```bash
cd sdk
poetry install
```

## Usage

```python
from sdk import AuthenticatedClient
from sdk.api_client.api.data_products import get_data_products_v2_data_products_get

client = AuthenticatedClient(base_url="https://your-portal.example.com", token="<token>")
result = get_data_products_v2_data_products_get.sync(client=client)
```

`sdk.api_client` mirrors the OpenAPI structure — models are in `sdk.api_client.models`, endpoints in `sdk.api_client.api.<resource>`.

## Authentication

`PortalAuth` handles token acquisition and caching. It supports two flows:

- **Device authorization** (default): prompts a human to approve via browser
- **Client credentials**: machine-to-machine, no human interaction

### Environment variables

| Variable | Description |
|---|---|
| `PORTAL_BASE_URL` | Base URL of your portal (e.g. `https://portal.example.com/api/`) |
| `PORTAL_CLIENT_ID` | OAuth client ID |
| `PORTAL_CLIENT_SECRET` | OAuth client secret |
| `PORTAL_TOKEN_URL` | Cognito token endpoint (`https://<domain>.amazoncognito.com/oauth2/token`) |
| `PORTAL_AUTH_MODE` | `""` for device flow (default) or `"client_credentials"` |
| `PORTAL_SCOPE` | OAuth scope (default: `"openid"`) |
| `PORTAL_DEV_MODE` | Set to `"true"` to skip auth entirely (returns empty token) |

### Example

```python
from sdk import AuthenticatedClient, PortalAuth
from sdk.api_client.api.data_products import get_data_product

client = PortalAuth().get_client()
result = get_data_product.sync(id=some_uuid, client=client)
```

Tokens are cached in `~/.portal/token.json` and refreshed automatically before expiry.
For client credentials mode, set `PORTAL_AUTH_MODE=client_credentials` — tokens are not persisted to disk.

## Reconcile loop (operator pattern)

`sdk.reconcile` provides a Kubernetes-operator-style reconcile loop for exploration
webhook events. Events for the same exploration are **coalesced** (two events for one
id trigger a single reconcile), enqueued with a short **debounce delay**, processed by a
pool of **workers** (one exploration is never reconciled twice concurrently), and
**requeued with exponential backoff** on failure.

Reconciliation is **level-based**: your reconciler receives only the exploration id and
re-fetches current state itself.

```python
from uuid import UUID

from sdk import Reconciler, ReconcileManager, ReconcileEventHandler

class ExplorationReconciler(Reconciler):
    async def reconcile(self, exploration_id: UUID):
        # Re-fetch the current state of the exploration and converge towards it.
        # Return None on success, or an exception on failure. Will automatically be retried on failure with exponential backoff.
        ...

manager = ReconcileManager(ExplorationReconciler(), default_delay=30.0, num_workers=4)
manager.start()  # call from within a running asyncio loop

handler = ReconcileEventHandler(manager)
# Wire handler.dispatch_routing(request) into your FastAPI webhook endpoint.
# Call `await manager.stop()` on shutdown.
```

Every `exploration.created`, `exploration.updated` and `exploration.deleted` webhook
enqueues the exploration id and returns immediately with `{"status": "queued"}`.

## Regenerating the API client

Run this after the OpenAPI spec changes (e.g. after `task update:open-api-spec` at the repo root):

```bash
task generate:client
```

This regenerates `sdk/api_client/` from the openapi spec in docs. Do not edit files inside `sdk/api_client/` by hand. The sdk client is also automatically regenerated if changes to the openapi spec are detected.
