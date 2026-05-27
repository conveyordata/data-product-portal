# Event Payload Scoping

## Context and Problem Statement

ADR-0013 introduced enriched V2 webhook events. The current implementation embeds full API response objects (e.g. `GetDataProductResponse`) directly in each event. Two problems follow:

1. **Delete events are broken for provisioners.** A provisioner receiving `data_product.deleted` cannot call back to fetch the object it needs to tear down infrastructure — the object is already gone.
2. **Tight coupling to the API layer.** API response shapes change as the portal evolves. Any refactor silently breaks provisioner consumers who depend on those shapes.

Events are a public contract between the portal and external provisioners. They need their own stable models.

## Decision Drivers

* Provisioners must be able to act on delete events without calling back to the portal
* `output_port.link_approved` must carry enough context for a provisioner to issue an access grant (e.g. `GRANT SELECT ON SCHEMA`) without round-trips to fetch both sides
* Event payloads should not grow stale when API response models are refactored
* Payloads should be minimal — include what provisioners act on, not display metadata

## Considered Options

* **Option 1: ID-only events + soft deletes** — events carry only entity IDs; deleted objects stay queryable via a `deleted_at` flag; provisioners hydrate via the SDK
* **Option 2: Full API response objects embedded** — continue embedding `GetDataProductResponse` and friends directly (current approach)
* **Option 3: Dedicated per-event payload models** — define a small set of purpose-built payload models independent of the API response layer

## Decision Outcome

**Chosen option:** *Option 3: Dedicated per-event payload models*.

Soft deletes (Option 1) require a cross-cutting DB schema change and still leave the provisioner dependent on SDK round-trips. Full API objects (Option 2) solve the delete problem accidentally but couple the event contract to internal API shapes. Dedicated models give provisioners a stable, right-sized contract that survives internal refactors.

### Confirmation

- A set of purpose-built Pydantic payload models is defined in `backend/app/core/webhooks/` (separate from `schema_response.py` files)
- All `V2Event` subclasses in `events.py` reference these payload models, not API response models
- The event catalogue in Appendix A governs what each event carries

---

## Pros and Cons of the Options

### Option 1: ID-only events + soft deletes

* **Good, because** payloads are minimal and provisioners fetch only what they need
* **Bad, because** soft deletes require schema migrations across multiple tables and add query complexity throughout the codebase
* **Bad, because** provisioners still need SDK round-trips for every event, including delete events

### Option 2: Full API response objects embedded

* **Good, because** zero new models to define or maintain
* **Bad, because** API response shapes change for unrelated reasons and silently break provisioner consumers
* **Bad, because** payloads include display fields (`about`, `usage`, `tags`) that provisioners never use

### Option 3: Dedicated per-event payload models

* **Good, because** event schema is decoupled from the API layer — internal refactors don't break consumers
* **Good, because** delete events embed full object state at dispatch time, solving the teardown problem without soft deletes
* **Good, because** `output_port.link_approved` can embed both sides (requesting DP + output port) with their technical assets, eliminating round-trips for access grants
* **Neutral, because** requires upfront scoping of each event (see Appendix A)
* **Bad, because** two model hierarchies (API responses + event payloads) must be maintained in parallel

---

## Appendix A: Event Payload Catalogue

### Building Blocks

Four reusable payload models compose all event payloads:

**`DataProductPayload`** — `id`, `name`, `namespace`, `domain_id`, `domain_name`, `type_id`, `type_name`, `lifecycle_name` (nullable), `status` //TODO: status, lifecycle_name

**`OutputPortPayload`** — `id`, `name`, `namespace`, `data_product_id`, `access_type`, `status`, `settings` //TODO: Settings needed?, status

**`TechnicalAssetPayload`** — `id`, `name`, `namespace`, `platform_id`, `service_id`, `configuration`, `status` //TODO: status

**`RoleAssignmentPayload`** — `id`, `user_id`, `user_email`, `role`

### Rules for Technical Asset Inclusion

| Situation | Include TAs? | Reason |
|---|---|---|
| Delete events | Always | Object is gone after dispatch; teardown needs config |
| Create events | Never | No TAs exist at creation time |
| Update / status / setting events | No | Object still exists; SDK round-trip acceptable |
| `output_port.link_approved` | Yes, both sides | Provisioner needs requesting DP's login TA + output port's schema TA to issue access grant |

### Data Product Events

| Event | Payload |
|---|---|
| `data_product.created` | `DataProductPayload` |
| `data_product.updated` | `DataProductPayload` |
| `data_product.deleted` | `DataProductPayload` + `technical_assets: list[TechnicalAssetPayload]` | //TODO: what is the impact of deleting a data product and all it's output ports
| `data_product.about_updated` | `DataProductPayload` | //TODO: weird that the about is not included and needs to be fetched. Ok for me
| `data_product.status_updated` | `DataProductPayload` |
| `data_product.setting_changed` | `DataProductPayload` + `setting_id: str` | /TODO: weird that the about is not included and needs to be fetched. Why add the setting_id?
| `data_product.input_port_linked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` |
| `data_product.input_port_unlinked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` |
| `data_product.team_member_added` | `DataProductPayload` + `RoleAssignmentPayload` |
| `data_product.team_member_removed` | `DataProductPayload` + `RoleAssignmentPayload` |
| `data_product.team_member_updated` | `DataProductPayload` + `RoleAssignmentPayload` |

`input_port_linked/unlinked` fires on the requesting data product's side. `owning_data_product` identifies whose output port this is. Access grant/revoke is handled on the output port side via `link_approved`/`link_denied`.

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

`link_approved` is deliberately richer: the provisioner needs the requesting DP's technical asset (platform login) and the output port's technical assets (schema) to issue an access grant without SDK round-trips.

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

TA events always include `TechnicalAssetPayload` since the TA carries the platform config. `OutputPortPayload` is included only where the event concerns a TA↔port relationship.
