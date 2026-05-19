# Event Payload Scoping Design

**Date:** 2026-05-19
**Status:** Approved
**Related ADR:** docs/adr/0013-provisioner-architecture.md

---

## Problem

The current V2 webhook events embed full API response objects (e.g. `GetDataProductResponse`) directly in the event payload. This approach has two issues:

1. **Correctness**: Delete events lose queryable context — a provisioner that receives a `data_product.deleted` event cannot call back to fetch the object it needs to tear down infrastructure.
2. **Coupling**: API response shapes change independently of the event contract. Any refactor to an API response model silently breaks provisioner consumers.

Events are a **public API contract**. They need their own stable models, separate from the API response layer.

---

## Decision

Define dedicated event payload models that are independent of API response schemas. Each model includes only the fields a provisioner needs to act on that event — no display metadata (`about`, `usage`, `tags`).

---

## Building Blocks

Four reusable payload models compose all events:

### `DataProductPayload`
```
id, name, namespace, domain_id, domain_name,
type_id, type_name, lifecycle_name (nullable), status
```

### `OutputPortPayload`
```
id, name, namespace, data_product_id,
access_type, status, settings: list[SettingValue]
```

### `TechnicalAssetPayload`
```
id, name, namespace, platform_id, service_id,
configuration, status
```

### `RoleAssignmentPayload`
```
id, user_id, user_email, role
```

---

## Rules for Technical Asset Inclusion

| Situation | Include TAs? | Reason |
|---|---|---|
| Delete events | Always | Object is gone after dispatch; teardown needs config |
| Create events | Never | No TAs exist at creation time |
| Update / status / setting events | No | Object still exists; SDK round-trip acceptable |
| `output_port.link_approved` | Yes, both sides | Provisioner needs requesting DP's login TA + output port's schema TA to issue access grant |

---

## Event Catalogue

### Data Product Events

| Event | Payload |
|---|---|
| `data_product.created` | `DataProductPayload` |
| `data_product.updated` | `DataProductPayload` |
| `data_product.deleted` | `DataProductPayload` + `technical_assets: list[TechnicalAssetPayload]` |
| `data_product.about_updated` | `DataProductPayload` |
| `data_product.status_updated` | `DataProductPayload` |
| `data_product.setting_changed` | `DataProductPayload` + `setting_id: str` |
| `data_product.input_port_linked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` |
| `data_product.input_port_unlinked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` |
| `data_product.team_member_added` | `DataProductPayload` + `RoleAssignmentPayload` |
| `data_product.team_member_removed` | `DataProductPayload` + `RoleAssignmentPayload` |
| `data_product.team_member_updated` | `DataProductPayload` + `RoleAssignmentPayload` |

Notes:
- `input_port_linked/unlinked` fires on the **requesting** data product's side. `owning_data_product` identifies whose output port this is. No TAs needed here — access grant/revoke is handled on the output port side via `link_approved`/`link_denied`.

### Output Port Events

| Event | Payload |
|---|---|
| `output_port.created` | `DataProductPayload` + `OutputPortPayload` |
| `output_port.updated` | `DataProductPayload` + `OutputPortPayload` |
| `output_port.deleted` | `DataProductPayload` + `OutputPortPayload` + `technical_assets: list[TechnicalAssetPayload]` |
| `output_port.about_updated` | `DataProductPayload` + `OutputPortPayload` |
| `output_port.status_updated` | `DataProductPayload` + `OutputPortPayload` |
| `output_port.setting_changed` | `DataProductPayload` + `OutputPortPayload` + `setting_id: str` |
| `output_port.link_approved` | `requesting_data_product: DataProductPayload` + `requesting_data_product_technical_assets: list[TechnicalAssetPayload]` + `output_port: OutputPortPayload` + `output_port_technical_assets: list[TechnicalAssetPayload]` + `owning_data_product: DataProductPayload` |
| `output_port.link_denied` | `requesting_data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` |

Notes:
- `link_approved` is deliberately richer than other events. The provisioner needs the requesting DP's technical asset (their platform login) and the output port's technical assets (the schema to grant access on) to issue an access grant without extra round-trips.

### Technical Asset Events

| Event | Payload |
|---|---|
| `technical_asset.created` | `DataProductPayload` + `TechnicalAssetPayload` |
| `technical_asset.updated` | `DataProductPayload` + `TechnicalAssetPayload` |
| `technical_asset.deleted` | `DataProductPayload` + `TechnicalAssetPayload` |
| `technical_asset.status_updated` | `DataProductPayload` + `TechnicalAssetPayload` |
| `technical_asset.linked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` |
| `technical_asset.link_approved` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` |
| `technical_asset.link_denied` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` |
| `technical_asset.unlinked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` |

Notes:
- TA events always include `TechnicalAssetPayload` since the TA itself carries the platform config. The `DataProductPayload` provides ownership context. `OutputPortPayload` is included only where the event is about a TA↔port relationship.

---

## What This Enables

- **Delete safety**: provisioners can tear down infrastructure without calling back to a deleted object.
- **Link access grants**: `output_port.link_approved` carries enough context on both sides for a provisioner to issue a database grant without any SDK round-trips.
- **Stable contract**: payload models are independent of API response shapes, so API refactors don't silently break provisioner consumers.
- **Expandable**: fields can be added to payload models as new provisioner use cases emerge.
