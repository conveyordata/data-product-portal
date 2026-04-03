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

auth = PortalAuth()
client = AuthenticatedClient(
    base_url="https://portal.example.com",
    token=auth.get_access_token(),
)
result = get_data_product.sync(id=some_uuid, client=client)
```

Tokens are cached in `~/.portal/token.json` and refreshed automatically before expiry.
For client credentials mode, set `PORTAL_AUTH_MODE=client_credentials` — tokens are not persisted to disk.

## Regenerating the API client

Run this after the OpenAPI spec changes (e.g. after `task update:open-api-spec` at the repo root):

```bash
task generate:client
```

This filters the spec to v2 endpoints, regenerates `sdk/api_client/`, and removes the intermediate spec file. Do not edit files inside `sdk/api_client/` by hand.
