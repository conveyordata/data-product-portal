# Event Payload Scoping

## Context and Problem Statement

ADR-0013 introduced enriched V2 webhook events. The current implementation embeds full API response objects (e.g. `GetDataProductResponse`) directly in each event. Two problems follow:

1. **Delete events are broken for provisioners.** A provisioner receiving `data_product.deleted` cannot call back to fetch the object — it is already gone. Cascading deletes make this worse: when a data product is removed, its output ports, technical assets, and the consumer links pointing at them all disappear in the same transaction, so a provisioner cannot even discover which downstream grants need to be revoked.
2. **Tight coupling to the API layer.** API response shapes change as the portal evolves for unrelated reasons (frontend reshaping, new display fields). Any refactor silently breaks provisioner consumers who depend on those shapes.

Events are a public contract between the portal and external provisioners. They need their own stable models, sized to the actual work a provisioner has to do.

A worked example for an AWS S3-backed platform — covering every event in the catalogue and the information a provisioner needs to act on it — is captured in [`reference/use-case-aws-s3-provisioner.md`](reference/use-case-aws-s3-provisioner.md). It is one example among several possible platform integrations (Snowflake, Databricks, BigQuery, …); the catalogue below is informed by this exercise and is expected to be revalidated against new platform use cases as they are written.

## Decision Drivers

- Provisioners must be able to act on delete events without calling back to the portal, including for cascade-deleted relationships (consumers of a deleted TA, output ports of a deleted DP, …).
- `output_port.link_approved` and `technical_asset.linked` must carry enough context for a provisioner to issue an access grant (e.g. `GRANT SELECT ON SCHEMA`, S3 IAM policy update) without two-sided round-trips.
- Events must be self-contained for any decision the provisioner branches on. Where behaviour differs by state — PENDING vs APPROVED link, PENDING vs ACTIVE TA, old vs new status — that state must be on the event.
- Event payloads should not grow stale when API response models are refactored.
- Payloads should be minimal — include what provisioners act on, not display metadata (`about`, `usage`, free-text descriptions).

## Considered Options

- **Option 1: ID-only events + soft deletes** — events carry only entity IDs; deleted objects stay queryable via a `deleted_at` flag; provisioners hydrate via the SDK.
- **Option 2: Full API response objects embedded** — continue embedding `GetDataProductResponse` and friends directly (current approach).
- **Option 3: Dedicated per-event payload models** — define a small set of purpose-built payload models independent of the API response layer.
- **Option 4: ID-only events + finalizers (Kubernetes-style)** — events carry only IDs; deletes go through a finalizer protocol where the portal marks an object for deletion, waits for every registered provisioner to run teardown and remove its finalizer, and only then completes the delete.
- **Option 5**: To facilitate easy deletes or migrations for domain for example, we could guide people to keep the state of their latest "apply". For example if the provisioner created an s3 bucket or location for a data product, it should keep that in a state object (dynamodb or ssm parameter), that way when the domain changes you can check the state object, see the name of the bucket and see it needs changing. This also helps with a delete since you know keep track of every infra component for an object
- **Option 6**: to facicilate deletes a delete product should also trigger delete events for all Technical assets and Output ports and links. 

## Decision Outcome

**Chosen option:** *Option 3: Dedicated per-event payload models*.

Soft deletes (Option 1) require a cross-cutting DB schema change and still leave the provisioner dependent on SDK round-trips for every event — including the hot paths (`link_approved`, `technical_asset.linked`) where two-sided hydration is exactly what the provisioner needs. Full API objects (Option 2) accidentally solve the delete problem but couple the event contract to internal API shapes and ship a lot of display metadata the provisioner never touches.

Finalizers (Option 4) are conceptually clean — Kubernetes uses the same pattern to give controllers a chance to clean up before an object is removed — but they invert the operational model. Portal deletes become asynchronous and block on external systems: UI affordances like "delete this data product" no longer reflect an immediate state change, partial failures are easy (one provisioner stuck, the object stuck with it). Beyond the delete case, non-delete events would still need SDK round-trips — the finalizer trick only buys delete semantics. Moving from fire-and-forget events to two-phase commit deletes is a significantly larger architectural step than this problem warrants.

Dedicated models give provisioners a stable, right-sized contract that survives internal refactors, keeps deletes fire-and-forget, and lets each event carry exactly the state needed for the provisioner's branching logic.

### Confirmation

- A set of purpose-built Pydantic payload models lives under `backend/app/core/webhooks/`, separate from the `schema_response.py` files.
- All `V2Event` subclasses in `events.py` reference these payload models, not API response models.
- The event catalogue in Appendix A governs what each event carries; deviations require a follow-up ADR.
- The AWS S3 use case in `reference/use-case-aws-s3-provisioner.md` runs against the catalogue end-to-end without provisioner-side SDK round-trips on delete or link-approval paths.

---

## Pros and Cons of the Options

### Option 1: ID-only events + soft deletes

- **Good, because** payloads are minimal and provisioners fetch only what they need.
- **Good, because** the delete problem dissolves: the object stays addressable via the SDK after the delete event.
- **Bad, because** soft deletes require schema migrations across many tables and add `deleted_at` filtering throughout every query in the codebase.
- **Bad, because** provisioners still need SDK round-trips for every event, including on the hot paths (`link_approved`, `technical_asset.linked`) where two-sided hydration would otherwise be a single payload.
- **Bad, because** cascading deletes still need a custom solution — a deleted data product's output ports, TAs, and consumer links must remain reachable too, multiplying the soft-delete surface area.

### Option 2: Full API response objects embedded

- **Good, because** zero new models to define or maintain.
- **Bad, because** API response shapes change for unrelated reasons (new display fields, schema reshaping for the frontend) and silently break provisioner consumers.
- **Bad, because** payloads include display fields (`about`, `usage`, `tags`) that provisioners never use.
- **Bad, because** delete events are still broken for cascade-deleted children (consumers of a TA, TAs of a deleted output port).

### Option 3: Dedicated per-event payload models

- **Good, because** event schema is decoupled from the API layer — internal refactors do not break consumers.
- **Good, because** delete events can embed full state at dispatch time, solving teardown without soft deletes or finalizers.
- **Good, because** `output_port.link_approved` and `technical_asset.linked` can embed both sides (requesting DP + output port + relevant TAs + existing consumers), eliminating round-trips on the hot path.
- **Good, because** branching state (link status APPROVED vs PENDING, TA status transitions) can be carried explicitly on the event.
- **Neutral, because** requires upfront scoping of each event (see Appendix A) and a worked use case to validate the scope.
- **Bad, because** two model hierarchies (API responses + event payloads) must be maintained in parallel; care is needed to keep them from drifting back into coupling.
- 
- **Bad, because** Payloads might still not include what you need in a provisioner, it is very hard to product. So you might still need to use the SDK to fetch extra information. Which is possible for update, but not for delete

### Option 4: ID-only events + finalizers (Kubernetes-style)

- **Good, because** the event contract stays tiny — only IDs travel on the wire.
- **Good, because** the delete-cascade problem dissolves cleanly: deletes are explicitly blocked until every provisioner signs off, so nothing is gone before teardown finishes.
- **Good, because** the pattern is well understood from Kubernetes; provisioners that already think in terms of controllers map onto it directly.
- **Bad, because** portal deletes become asynchronous and block on external systems, changing the UX contract of every delete affordance in the product.
- **Bad, because** events still need SDK round-trips; the finalizer trick only addresses delete semantics.
- **Bad, because** moving from fire-and-forget events to two-phase-commit deletes is a much larger architectural shift than this ADR is scoped to make.

---

## Appendix A: Event Payload Catalogue

The shape below is the contract: which entities each event ships, and which extras a provisioner cannot derive at dispatch time. Additions to the "extras" require either a new platform use case showing the need, or a follow-up ADR.

### Building Blocks

**`DataProductPayload`** — `id`, `name`, `namespace`, `domain_id`, `domain_name`, `type_id`, `type_name`, `lifecycle_name` (nullable), `status`, `settings: list[SettingPayload]`

**`ExplorationPayload`** — `id`, `name`, `namespace`, `status`

**`OutputPortPayload`** — `id`, `name`, `namespace`, `data_product_id`, `access_type` (restricted / unrestricted), `status`, `settings: list[SettingPayload]`

**`TechnicalAssetPayload`** — `id`, `name`, `namespace`, `platform_id`, `service_id`, `configuration`, `status`, `mapping` (default / custom)

**`RoleAssignmentPayload`** — `id`, `user_id`, `user_email`, `role`

**`SettingPayload`** — `id`, `name`, `value`

### Rules for Cascade and State Inclusion

The general rule: an event must be self-contained for any branching decision a provisioner needs to make on it.

| Situation | Include extra state? | Reason |
|---|---|---|
| Create events | No | No prior state, no consumers, nothing to embed. |
| Update / status / settings events on a live object | No | Object still exists; SDK round-trip acceptable. |
| Delete events | Yes — full teardown context | Object and its cascades are gone after dispatch; provisioner cannot fetch. |
| Link state transitions (linked / unlinked) | Yes — current link status | Provisioner branches between APPROVED and PENDING; status must be on the event. |
| Status transitions where old state matters | Yes — old + new | E.g. TA PENDING→ACTIVE vs ACTIVE→ARCHIVED have opposite infrastructure effects. |
| Link approval / TA linked | Yes — both sides + existing consumers | A single event must let the provisioner grant access without round-trips. |

### Data Product Events

| Event | Payload | Notes |
|---|---|---|
| `data_product.created` | `DataProductPayload` + `team_members: list[RoleAssignmentPayload]` | Trust policy is populated at creation; the initial owner(s) must arrive on this event, not via follow-up `team_member_added` events. |
| `data_product.updated` | `DataProductPayload` (old + new) | Domain change is the disruptive case; the old domain must be known for migration. |
| `data_product.deleted` | `DataProductPayload` + `technical_assets: list[TechnicalAssetPayload]` + per-TA `consumers: list[DataProductPayload]` | DB cascade wipes output ports, TAs, and consumer links; all must be embedded. Consumers are listed per TA because different consumer sets may attach to each TA via different output ports. |
| `data_product.about_updated` | `DataProductPayload` | About is fetched via SDK if needed (e.g. by an AI-agent integration that uses it as a system prompt). |
| `data_product.status_updated` | `DataProductPayload` (with new status) | |
| `data_product.setting_changed` | `DataProductPayload` + `setting: SettingPayload` (old + new value) | Provisioner branches on which setting changed and how; shipping the full setting avoids a round-trip on the very next instruction. |
| `data_product.team_member_added` | `DataProductPayload` + `RoleAssignmentPayload` | |
| `data_product.team_member_removed` | `DataProductPayload` + `RoleAssignmentPayload` | |
| `data_product.team_member_updated` | `DataProductPayload` + `RoleAssignmentPayload` (with old + new role) | Role transitions to/from non-integration roles drive trust-policy updates. |
| `data_product.input_port_linked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` + `link_status` (APPROVED / PENDING) | Without `link_status`, the provisioner cannot distinguish unrestricted (act now) from restricted (wait for approval). |
| `data_product.input_port_unlinked` | Same as `linked` + `link_status` at removal time | Without the status the provisioner cannot tell whether access was ever granted, and therefore whether anything needs revoking. |

`input_port_linked/unlinked` fires on the requesting data product's side. Access grants/revokes for restricted output ports are driven by `output_port.link_approved` / `link_denied`; unrestricted output ports are granted on the link event itself, which is why the link status must be on it.

### Exploration Events

Explorations have no output ports, no technical assets, and no settings; their payloads stay correspondingly small.

| Event | Payload | Notes |
|---|---|---|
| `exploration.created` | `ExplorationPayload` + `owner: RoleAssignmentPayload` | Trust policy needs the owner at creation. |
| `exploration.deleted` | `ExplorationPayload` | No cascaded children to embed. |
| `exploration.input_port_linked` | `exploration: ExplorationPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` + `link_status` | Mirrors `data_product.input_port_linked`. |
| `exploration.input_port_unlinked` | Same as `linked` + `link_status` at removal time | Mirrors `data_product.input_port_unlinked`. |

### Output Port Events

| Event | Payload | Notes |
|---|---|---|
| `output_port.created` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.updated` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.deleted` | `DataProductPayload` + `OutputPortPayload` + `technical_assets: list[TechnicalAssetPayload]` + `consumers: list[DataProductPayload]` | The TAs themselves survive (they belong to the DP) but the OP↔TA links and consumer links are gone after dispatch. |
| `output_port.about_updated` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.status_updated` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.setting_changed` | `DataProductPayload` + `OutputPortPayload` + `setting: SettingPayload` (old + new value) | |
| `output_port.link_approved` | `requesting_data_product: DataProductPayload` + `requesting_technical_assets: list[TechnicalAssetPayload]` + `output_port: OutputPortPayload` + `output_port_technical_assets: list[TechnicalAssetPayload]` + `owning_data_product: DataProductPayload` | Provisioner needs both sides — requesting DP's login TA + output port's schema TA — to issue an access grant without SDK round-trips. |
| `output_port.link_denied` | `requesting_data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` | No grants involved, no TAs needed. |
| `output_port.team_member_added` / `removed` / `updated` | `DataProductPayload` + `OutputPortPayload` + `RoleAssignmentPayload` | Currently no infrastructure action; future output-port-level grants would key off these. |

### Technical Asset Events

| Event | Payload | Notes |
|---|---|---|
| `technical_asset.created` | `DataProductPayload` + `TechnicalAssetPayload` | `mapping` discriminates default (initial status ACTIVE) from custom (initial status PENDING). |
| `technical_asset.updated` | `DataProductPayload` + `TechnicalAssetPayload` | S3-like platforms can ignore; included for parity. |
| `technical_asset.status_updated` | `DataProductPayload` + `TechnicalAssetPayload` (old + new status) | Provisioner needs the old status to distinguish activation (PENDING→ACTIVE) from archival (ACTIVE→ARCHIVED). |
| `technical_asset.deleted` | `DataProductPayload` + `TechnicalAssetPayload` + per-OP-link `consumers: list[DataProductPayload]` | The TA itself is gone, and so are the OP-link rows and the consumer links behind each one. |
| `technical_asset.linked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` + `consumers: list[DataProductPayload]` | Existing approved consumers of the OP must receive a grant immediately on this event. |
| `technical_asset.unlinked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` + `consumers: list[DataProductPayload]` | Existing approved consumers of the OP must have their grant revoked if they have no other path to this TA. |

TA events always include `TechnicalAssetPayload` since the TA carries the platform configuration. `OutputPortPayload` is included only where the event concerns a TA↔OP relationship.
