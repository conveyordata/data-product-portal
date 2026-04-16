# Provisioner Architecture: Backend Event Adapter + Abstract Base Class SDK

## How It Works Today

The Portal backend fires a generic webhook after every mutating API call. The payload is a raw forward of the HTTP exchange:

```json
{
  "method": "POST",
  "url": "/api/v2/data_products",
  "query": {},
  "response": "{\"id\": \"abc-123\", \"name\": \"My Product\"}",
  "status_code": 200
}
```

A provisioner is a separate HTTP service that receives all of these at a single `POST /` endpoint. To handle an event, it must:

1. Inspect `method` + `url` to figure out what happened
2. Parse the raw `response` string to extract an entity ID
3. Call back to the Portal to fetch the full object before doing any real work

The demo provisioner (`demo/basic/provisioner/`) implements a custom `Router` class to handle this routing. There is no typed contract, no documented event format, and no helper for calling back into the Portal. Each new provisioner starts by copying the demo and reverse-engineering the internal `Router`.

## What We're Building

Two changes work together to fix this.

**1. Backend event adapter** — Instead of forwarding the raw HTTP exchange, the backend maps each API call to a named domain event with the full object embedded:

```json
{
  "event": "data_product.created",
  "data_product": { ...full DataProduct object... }
}
```

This lives in the backend so all provisioners benefit immediately, regardless of whether they use the SDK.

**2. Provisioner SDK (`dpp-provisioner-sdk`)** — A Python package that consumes these enriched events and routes them to typed hook methods. Authors subclass `BaseProvisioner` and override only the hooks relevant to their platform:

```python
from dpp_provisioner import BaseProvisioner, PortalClient
from dpp_provisioner.models import DataProduct

class MyProvisioner(BaseProvisioner):
    def on_create_data_product(self, data_product: DataProduct) -> None:
        lifecycle = self.client.get_lifecycle("Ready")
        self.client.update_data_product_status(data_product.id, lifecycle.id)

client = PortalClient(
    api_url=os.environ["DPP_API_URL"],
    api_token=os.environ["DPP_API_TOKEN"],
)
app = MyProvisioner(client=client).get_app()

# serve with: uvicorn main:app --port 6060
```

Authors no longer inspect raw payloads, regex-match URLs, or call back to get full objects — the event carries everything they need.

## Decision Drivers

* **Developer experience**: new provisioner authors need a clear, discoverable starting point
* **Type safety**: handler functions receive rich objects, not raw dicts
* **Coverage**: all mutating Portal events addressable via named hooks
* **Composability**: SDK produces a standard FastAPI `app` — authors control how it is served
* **Transport flexibility**: hooks must be transport-agnostic so they work with webhooks today and a message queue tomorrow
* **Consistency**: align with the base-class pattern established in ADR-0009

## Decision 1: Where to Put the Event Adapter

**Chosen: in the backend.**

The alternative is to put adaptation logic in the SDK or in each provisioner. But since events today carry only a raw API response, every provisioner would need to call back to the Portal to hydrate full objects — SDK or not. Putting the adapter in the backend solves this once, for all provisioners, regardless of language or framework.

## Decision 2: SDK Shape — Abstract Base Class vs. Fluent Builder

**Chosen: Abstract Base Class (`BaseProvisioner`)**

Both options expose `.get_app()`, following the pattern used by [Agno](https://docs.agno.com): the SDK returns a plain FastAPI application rather than owning the server lifecycle. Authors pass the app to uvicorn, mount it inside an existing app, or add middleware — the SDK handles routing and deserialisation only.

The ABC wins over the fluent builder because:

- `self.client` is available in all hooks without threading it through parameters
- All hook signatures appear in the base class — IDE autocomplete guides authors to what's available
- Default no-op implementations mean unimplemented hooks are silently skipped
- Consistent with the base-class plugin pattern in ADR-0009

### Fluent Builder (not chosen)

```python
app = (
    Provisioner(client=client)
    .on_create_data_product(handle_create)
    .on_approve_link(handle_approve)
    .get_app()
)
```

Good: handlers are plain functions, easier to unit-test in isolation. No class inheritance required.
Bad: no natural home for shared state; gaps in hook coverage are silent; discoverability depends on docs rather than IDE autocomplete.

## Transport Extensibility

Currently events arrive via **synchronous HTTP webhooks**: the Portal calls the provisioner directly after each mutation. This is simple but fragile — if the provisioner is temporarily unavailable, the event is lost.

Hook method signatures (`on_create_data_product`, `on_approve_link`, etc.) contain no HTTP coupling, so a queue-based transport (SQS, Kafka) can be added in future without changing any hook implementations. Only the transport layer changes.

```
┌──────────────────────────────────────────────────────────┐
│                   BaseProvisioner                        │
│   on_create_data_product(dp: DataProduct) → None         │
│   on_approve_link(dp, op, link) → None                   │
│   ...                                                    │
└────────────────────────┬─────────────────────────────────┘
                         │ dispatches to hooks
          ┌──────────────┴──────────────┐
          │                             │
  ┌───────▼────────┐           ┌────────▼────────┐
  │  WebhookRunner │           │  QueueConsumer  │  ← future
  │  get_app()     │           │  (SQS / Kafka)  │
  │  (FastAPI app) │           │                 │
  └────────────────┘           └─────────────────┘
```

## Confirmation

- Backend enriches webhook payloads with full domain objects before dispatching to provisioners
- Delivered as installable Python package `dpp-provisioner-sdk`
- Demo provisioner (`demo/basic/provisioner/`) rewritten to subclass `BaseProvisioner`
- Package README shows a minimal from-scratch example

---

## Appendix A: Full Event Catalogue

All hooks receive typed objects rather than raw dicts. The `DataProduct` context is always present; `OutputPort` and `TechnicalAsset` are included where the event is scoped to them.

### Data Product Events

| Hook | Trigger endpoint |
|------|-----------------|
| `on_create_data_product(dp: DataProduct)` | `POST /api/v2/data_products` |
| `on_update_data_product(dp: DataProduct)` | `PUT /api/v2/data_products/{id}` |
| `on_delete_data_product(dp: DataProduct)` | `DELETE /api/v2/data_products/{id}` |
| `on_update_data_product_about(dp: DataProduct)` | `PUT /api/v2/data_products/{id}/about` |
| `on_update_data_product_status(dp: DataProduct)` | `PUT /api/v2/data_products/{id}/status` |
| `on_add_team_member(dp: DataProduct, assignment: RoleAssignment)` | `POST /api/v2/authz/role_assignments/data_product` |
| `on_remove_team_member(dp: DataProduct, assignment: RoleAssignment)` | `DELETE /api/v2/authz/role_assignments/data_product/{id}` |
| `on_change_setting(dp: DataProduct, setting_id: str)` | `POST /api/v2/data_products/{id}/settings/{setting_id}` |
| `on_link_input_port(dp: DataProduct, link: InputPortLink)` | `POST /api/v2/data_products/{id}/link_input_ports` |
| `on_unlink_input_port(dp: DataProduct, link: InputPortLink)` | `DELETE /api/v2/data_products/{id}/input_ports/{input_port_id}` |

### Output Port Events

| Hook | Trigger endpoint |
|------|-----------------|
| `on_create_output_port(dp: DataProduct, op: OutputPort)` | `POST /api/v2/data_products/{id}/output_ports` |
| `on_update_output_port(dp: DataProduct, op: OutputPort)` | `PUT /api/v2/data_products/{id}/output_ports/{id}` |
| `on_delete_output_port(dp: DataProduct, op: OutputPort)` | `DELETE /api/v2/data_products/{id}/output_ports/{id}` |
| `on_update_output_port_about(dp: DataProduct, op: OutputPort)` | `PUT /api/v2/data_products/{id}/output_ports/{id}/about` |
| `on_update_output_port_status(dp: DataProduct, op: OutputPort)` | `PUT /api/v2/data_products/{id}/output_ports/{id}/status` |
| `on_approve_link(dp: DataProduct, op: OutputPort, link: InputPortLink)` | `POST .../output_ports/{id}/input_ports/approve` |
| `on_change_output_port_setting(dp: DataProduct, op: OutputPort, setting_id: str)` | `POST .../output_ports/{id}/settings/{setting_id}` |

### Technical Asset Events

| Hook | Trigger endpoint |
|------|-----------------|
| `on_create_technical_asset(dp: DataProduct, ta: TechnicalAsset)` | `POST /api/v2/data_products/{id}/technical_assets` |
| `on_update_technical_asset(dp: DataProduct, ta: TechnicalAsset)` | `PUT .../technical_assets/{id}` |
| `on_delete_technical_asset(dp: DataProduct, ta: TechnicalAsset)` | `DELETE .../technical_assets/{id}` |
| `on_update_technical_asset_status(dp: DataProduct, ta: TechnicalAsset)` | `PUT .../technical_assets/{id}/status` |
| `on_link_technical_asset(dp: DataProduct, op: OutputPort, ta: TechnicalAsset)` | `POST .../output_ports/{id}/technical_assets/add` |
| `on_approve_technical_asset_link(dp: DataProduct, op: OutputPort, ta: TechnicalAsset)` | `POST .../technical_assets/approve_link_request` |
| `on_deny_technical_asset_link(dp: DataProduct, op: OutputPort, ta: TechnicalAsset)` | `POST .../technical_assets/deny_link_request` |
| `on_unlink_technical_asset(dp: DataProduct, op: OutputPort, ta: TechnicalAsset)` | `DELETE .../technical_assets/remove` |

---

## Appendix B: SDK Pseudocode

### `PortalClient` — Portal API helper

`PortalClient` is constructed explicitly with the Portal URL and an API token. Authors create it themselves and pass it to the provisioner — there is no magic environment-variable bootstrapping hidden inside the class.

```python
class PortalClient:
    def __init__(self, api_url: str, api_token: str) -> None: ...

    # Data products
    def get_data_product(self, id: str) -> DataProduct: ...
    def get_lifecycle(self, name: str) -> Lifecycle: ...
    def update_data_product_status(self, data_product_id: str, lifecycle_id: str) -> None: ...

    # Output ports
    def get_output_port(self, data_product_id: str, output_port_id: str) -> OutputPort: ...

    # Technical assets
    def create_technical_asset(self, data_product_id: str, payload: TechnicalAssetCreate) -> TechnicalAsset: ...
    def update_technical_asset_status(self, data_product_id: str, ta_id: str, status: str) -> None: ...

    # Platform configs
    def get_platform_configs(self) -> list[PlatformServiceConfig]: ...
```

### `BaseProvisioner`

```python
from abc import ABC
from fastapi import FastAPI

class BaseProvisioner(ABC):
    def __init__(self, client: PortalClient) -> None:
        self.client = client

    def get_app(self) -> FastAPI:
        """Return a FastAPI app with all webhook routes wired to hook methods.

        Serve it however you like:
            uvicorn main:app --port 6060
        or mount it on an existing FastAPI app:
            parent_app.mount("/provisioner", provisioner.get_app())
        """
        ...

    # --- Data Product ---
    def on_create_data_product(self, data_product: DataProduct) -> None: pass
    def on_update_data_product(self, data_product: DataProduct) -> None: pass
    def on_delete_data_product(self, data_product: DataProduct) -> None: pass
    def on_update_data_product_about(self, data_product: DataProduct) -> None: pass
    def on_update_data_product_status(self, data_product: DataProduct) -> None: pass
    def on_add_team_member(self, data_product: DataProduct, assignment: RoleAssignment) -> None: pass
    def on_remove_team_member(self, data_product: DataProduct, assignment: RoleAssignment) -> None: pass
    def on_change_setting(self, data_product: DataProduct, setting_id: str) -> None: pass
    def on_link_input_port(self, data_product: DataProduct, link: InputPortLink) -> None: pass
    def on_unlink_input_port(self, data_product: DataProduct, link: InputPortLink) -> None: pass

    # --- Output Port ---
    def on_create_output_port(self, data_product: DataProduct, output_port: OutputPort) -> None: pass
    def on_update_output_port(self, data_product: DataProduct, output_port: OutputPort) -> None: pass
    def on_delete_output_port(self, data_product: DataProduct, output_port: OutputPort) -> None: pass
    def on_update_output_port_about(self, data_product: DataProduct, output_port: OutputPort) -> None: pass
    def on_update_output_port_status(self, data_product: DataProduct, output_port: OutputPort) -> None: pass
    def on_approve_link(self, data_product: DataProduct, output_port: OutputPort, link: InputPortLink) -> None: pass
    def on_change_output_port_setting(self, data_product: DataProduct, output_port: OutputPort, setting_id: str) -> None: pass

    # --- Technical Asset ---
    def on_create_technical_asset(self, data_product: DataProduct, technical_asset: TechnicalAsset) -> None: pass
    def on_update_technical_asset(self, data_product: DataProduct, technical_asset: TechnicalAsset) -> None: pass
    def on_delete_technical_asset(self, data_product: DataProduct, technical_asset: TechnicalAsset) -> None: pass
    def on_update_technical_asset_status(self, data_product: DataProduct, technical_asset: TechnicalAsset) -> None: pass
    def on_link_technical_asset(self, data_product: DataProduct, output_port: OutputPort, technical_asset: TechnicalAsset) -> None: pass
    def on_approve_technical_asset_link(self, data_product: DataProduct, output_port: OutputPort, technical_asset: TechnicalAsset) -> None: pass
    def on_deny_technical_asset_link(self, data_product: DataProduct, output_port: OutputPort, technical_asset: TechnicalAsset) -> None: pass
    def on_unlink_technical_asset(self, data_product: DataProduct, output_port: OutputPort, technical_asset: TechnicalAsset) -> None: pass
```
