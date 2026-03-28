# Provisioner Architecture: Fluent Builder vs. Abstract Base Class SDK

## Context and Problem Statement

The current provisioner (`demo/basic/provisioner/provisioner/main.py`) is a flat FastAPI application with no formal abstraction, no typed inputs, and no SDK. New provisioner authors must copy the demo, understand the internal `Router` class, and manually handle raw webhook payloads. There is no documented contract, no type safety, and no helper client for calling back into the Portal API.

This ADR proposes an SDK approach (`dpp-sdk`) that:

- Provides a clear, typed interface for all provisioner lifecycle events
- Wraps Portal API calls in a high-level client (`PortalClient`)
- Exposes a standard FastAPI `app` object that authors serve themselves

A key design principle, inspired by how [Agno](https://docs.agno.com) serves agents via `agent_os.get_app()`, is that the SDK returns a plain FastAPI application rather than owning the server lifecycle. Authors stay in control: they can pass the app to uvicorn, mount it inside an existing FastAPI app, add middleware, or combine it with other routes. The SDK handles routing and deserialisation; the author handles deployment.

## Decision Drivers

* **Developer experience**: new provisioner authors need a clear, discoverable starting point
* **Type safety**: handler functions receive rich objects, not raw dicts
* **Coverage**: all mutating Portal events should be addressable via named hooks
* **Composability**: the SDK produces a standard FastAPI `app` — authors control how it is served
* **Transport flexibility**: hook implementations must be transport-agnostic so they can be driven by webhooks today and a message queue tomorrow without code changes
* **Consistency**: align with the base-class pattern established in ADR-0009

## Considered Options

* **Option 1: Fluent Builder API** — a `Provisioner` object configured by chaining `.on_*()` calls, exposing `.get_app()`
* **Option 2: Abstract Base Class SDK** — a `BaseProvisioner` class that authors subclass, overriding only the hooks they need, exposing `.get_app()`

## Decision Outcome

**Chosen option:** *Option 2: Abstract Base Class SDK*. The base-class pattern provides a natural home for shared state (notably `self.client`), guarantees IDE autocomplete on all lifecycle methods, and is consistent with ADR-0009. Default no-op implementations mean authors implement only the hooks relevant to their platform. Both options expose `.get_app()` following the Agno pattern; the ABC wins on discoverability and shared-state ergonomics.

### Confirmation

- Delivered as installable Python package `dpp-provisioner-sdk`
- Demo provisioner (`demo/basic/provisioner/`) rewritten to subclass `BaseProvisioner`
- Package README shows a minimal from-scratch example

## Pros and Cons of the Options

### Option 1: Fluent Builder API

```python
from dpp_provisioner import Provisioner, PortalClient

client = PortalClient(api_url="https://portal.example.com", api_token="secret")
app = (
    Provisioner(client=client)
    .on_create_data_product(handle_create)
    .on_approve_link(handle_approve)
    .get_app()
)

# serve with: uvicorn main:app --port 6060
```

* **Good, because** handlers are plain functions — easy to unit-test in isolation
* **Good, because** no inheritance required; feels closer to a functional style
* **Good, because** `.get_app()` returns a plain FastAPI app — authors control serving
* **Bad, because** no natural home for shared state (`client`) — handlers need it via closure or explicit parameter
* **Bad, because** hard to enforce that required hooks are implemented; gaps are silent
* **Bad, because** discoverability depends on reading docs rather than IDE autocomplete on the object

### Option 2: Abstract Base Class SDK

```python
from dpp_provisioner import BaseProvisioner, PortalClient
from dpp_provisioner.models import DataProduct

class MyProvisioner(BaseProvisioner):
    def on_create_data_product(self, data_product: DataProduct) -> None:
        lifecycle = self.client.get_lifecycle("Ready")
        self.client.update_data_product_status(data_product.id, lifecycle.id)

client = PortalClient(api_url="https://portal.example.com", api_token="secret")
app = MyProvisioner(client=client).get_app()

# serve with: uvicorn main:app --port 6060
```

* **Good, because** `self.client` is available in all hooks without threading through parameters
* **Good, because** all hook signatures appear in the base class — IDE autocomplete guides authors
* **Good, because** consistent with ADR-0009 base-class plugin pattern
* **Good, because** default no-op implementations mean unimplemented hooks are safe to omit
* **Good, because** `.get_app()` returns a plain FastAPI app — authors control serving, middleware, and mounting
* **Neutral, because** requires Python class inheritance, which may be unfamiliar to some authors
* **Bad, because** harder to compose behaviour across multiple independent handler modules

---

## Transport Extensibility

Currently the SDK listens for events via **direct HTTP webhooks**: the Portal calls the provisioner's HTTP endpoint synchronously after each mutating API call. This is simple and requires no infrastructure beyond the provisioner process itself.

However, synchronous webhooks have a reliability gap: if the provisioner is temporarily unavailable, the event is lost. A future evolution is to route events through a **message queue** (e.g. AWS SQS, RabbitMQ, Kafka). In that model the Portal publishes events to the queue and provisioners consume them at their own pace — surviving restarts and handling retries automatically.

The `BaseProvisioner` hook interface is designed to be **transport-agnostic**. Hook method signatures (`on_create_data_product`, `on_approve_link`, etc.) are pure business logic with no coupling to HTTP. The transport layer — whether webhook receiver or queue consumer — is responsible for deserialising the payload and dispatching to the appropriate hook.

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

Authors write hooks once; swapping the transport does not require changes to hook implementations.

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

### `PortalClient` — configuration and Portal API helper

`PortalClient` is constructed explicitly with the Portal URL and an API token. Authors create it themselves and pass it to the provisioner constructor — there is no magic environment-variable bootstrapping hidden inside the class.

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

### Minimal from-scratch example

```python
import os
from dpp_provisioner import BaseProvisioner, PortalClient
from dpp_provisioner.models import DataProduct

class SimpleProvisioner(BaseProvisioner):
    def on_create_data_product(self, data_product: DataProduct) -> None:
        lifecycle = self.client.get_lifecycle("Ready")
        self.client.update_data_product_status(data_product.id, lifecycle.id)
        print(f"Provisioned: {data_product.name}")

client = PortalClient(
    api_url=os.environ["DPP_API_URL"],
    api_token=os.environ["DPP_API_TOKEN"],
)
app = SimpleProvisioner(client=client).get_app()

# Run with: uvicorn main:app --port 6060
```
