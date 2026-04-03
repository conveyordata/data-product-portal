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

## Regenerating the API client

Run this after the OpenAPI spec changes (e.g. after `task update:open-api-spec` at the repo root):

```bash
task generate:client
```

This filters the spec to v2 endpoints, regenerates `sdk/api_client/`, and removes the intermediate spec file. Do not edit files inside `sdk/api_client/` by hand.
