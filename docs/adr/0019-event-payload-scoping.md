# Event Payload Scoping

## Context and Problem Statement

ADR-0013 introduced enriched V2 webhook events. The current implementation embeds full API response objects (e.g. `GetDataProductResponse`) directly in each event. Two problems follow:

1. **Delete events are broken for provisioners.** A provisioner receiving `data_product.deleted` cannot call back to fetch the object — it is already gone. Cascading deletes make this worse: when a data product is removed, its output ports, technical assets, and the consumer links pointing at them all disappear in the same DB transaction, so a provisioner cannot even discover which downstream grants need to be revoked.
2. **Tight coupling to the API layer.** API response shapes change as the portal evolves for unrelated reasons (frontend reshaping, new display fields). Any refactor silently breaks provisioner consumers who depend on those shapes.

Events are a public contract between the portal and external provisioners. They need their own stable models, sized to the actual work a provisioner has to do.

A worked example for an AWS S3-backed platform — covering every event in the catalogue and the information a provisioner needs to act on it — is captured in [`reference/use-case-aws-s3-provisioner.md`](reference/use-case-aws-s3-provisioner.md). It is one example among several possible platform integrations (Snowflake, Databricks, BigQuery, …); the catalogue below is informed by this exercise and is expected to be revalidated against new platform use cases as they are written.

## Decision Drivers

- Provisioners must be able to act on delete events without calling back to the portal, including for cascade-deleted relationships (consumers of a deleted TA, output ports of a deleted DP, …).
- `output_port.link_approved` and `technical_asset.linked` must carry enough context for a provisioner to issue an access grant (e.g. `GRANT SELECT ON SCHEMA`, S3 IAM policy update) without two-sided round-trips.
- Events must be self-contained for any decision the provisioner branches on. Where behaviour differs by state — PENDING vs APPROVED link, PENDING vs ACTIVE TA, old vs new status — that state must be on the event.
- Event payloads should not grow stale when API response models are refactored.
- Payloads should be minimal — include what provisioners act on, not display metadata (`about`, `usage`, free-text descriptions).
- The approach must be evolvable: if minimal payloads turn out to miss information that provisioners need in practice, we should be able to move to a richer model (ID-only + SDK hydration, or finalizers) without throwing away the catalogue.

## Considered Options

- **Option 1: ID-only events + soft deletes** — events carry only entity IDs; deleted objects stay queryable via a `deleted_at` flag; provisioners hydrate via the SDK.
- **Option 2: Full API response objects embedded** — continue embedding `GetDataProductResponse` and friends directly (current approach).
- **Option 3: Dedicated per-event payload models** — define a small set of purpose-built payload models independent of the API response layer.
- **Option 4: ID-only events + finalizers (Kubernetes-style)** — events carry only IDs; deletes go through a finalizer protocol where the portal marks an object for deletion, waits for every registered provisioner to run teardown and remove its finalizer, and only then completes the delete.
- **Option 5: Provisioner-side state tracking** — guide provisioner authors to persist the state of their latest "apply" (e.g. in DynamoDB, an SSM parameter, or their own database). On deletes or migrations the provisioner reads its own state to discover what infrastructure it owns, instead of relying on the portal to ship full teardown context. This is provisioner-side guidance, not a portal contract change.
- **Option 6: Cascade event emission** — when a parent is deleted, the portal also emits delete/unlink events for every cascaded child (output ports, technical assets, link rows) before the database cascade commits. The parent's delete event therefore does not need to embed child state; each child arrives as its own event.

## Decision Outcome

**Chosen approach:** *Option 3 (dedicated per-event payload models) combined with Option 6 (cascade event emission on delete).*

Option 2 is rejected outright: it accidentally solves the delete problem but couples the event contract to internal API shapes and ships a lot of display metadata the provisioner never touches.

Options 1 and 4 are kept on the table as evolution paths, not as the starting point:

- **Option 1** dissolves the delete-cascade problem by leaving objects addressable after their delete event, but requires a cross-cutting `deleted_at` schema change and forces an SDK round-trip on every event — including hot paths like `link_approved` and `technical_asset.linked` where two-sided hydration is exactly what the provisioner needs.
- **Option 4** is conceptually clean — Kubernetes uses the same pattern to give controllers a chance to clean up before an object is removed — but it inverts the operational model. Portal deletes become asynchronous and block on external systems: UI affordances like "delete this data product" no longer reflect an immediate state change, partial failures are easy (one provisioner stuck, the object stuck with it). Beyond the delete case, non-delete events would still need SDK round-trips. Moving from fire-and-forget events to two-phase-commit deletes is a significantly larger architectural shift than this problem warrants today.

Option 3 on its own leaves cascading deletes awkward: a `data_product.deleted` event would need to embed every output port, every technical asset, and every consumer link in a single fat payload. Option 6 fixes this: the portal emits a delete or unlink event for each cascaded child *before* the parent's transaction commits, so each event stays small and each child is handled by its own handler.

This combination gives provisioners a stable, right-sized contract that survives internal refactors, keeps deletes fire-and-forget, and keeps every delete handleable on its own event. **Options 1, 3, and 4 are not mutually exclusive**: if we discover that minimal payloads cannot carry what provisioners actually need in some flow, we can migrate to ID-only events with SDK hydration, or to finalizers, without invalidating the catalogue defined below. Option 5 lives entirely on the provisioner side — the portal does not assume provisioners track their own state, but we will document the pattern as a recommendation because every provisioner needs some equivalent in practice.

### Confirmation

- A set of purpose-built Pydantic payload models lives under `backend/app/core/webhooks/`, separate from the `schema_response.py` files.
- All `V2Event` subclasses in `events.py` reference these payload models, not API response models.
- Cascaded deletes inside the portal emit one event per child entity (output port, technical asset, input port link) in addition to the parent delete event. Child events fire before the database cascade so that each event still carries the relevant child state.
- The event catalogue in Appendix A governs what each event carries; deviations require a follow-up ADR.
- The AWS S3 use case in `reference/use-case-aws-s3-provisioner.md` runs against the catalogue end-to-end without provisioner-side SDK round-trips on delete or link-approval paths.

## Related Operational Concerns

Three problems came up during review that this ADR does not solve but that any working event pipeline needs answers for. They are listed here so the payload design stays compatible with them.

### Event persistence and replay

A provisioner that is down for an hour, that crashes mid-handler, or that has been freshly deployed against an existing portal needs a way to recover. Webhooks alone (fire-and-forget HTTP) do not provide this.

- Persist every dispatched event in the portal database, addressable by monotonic ID and timestamp.
- Expose a pull endpoint (e.g. `GET /events?since=<id-or-timestamp>&max=<n>`) so provisioners can replay missed events after downtime, or replay everything after a provisioner-side bug.
- Push remains the primary delivery mechanism for the first iteration; the pull endpoint is an additive path. Long-poll semantics for the pull endpoint are a possible enhancement but not required initially.

This is a small change layered on top of the current webhook implementation and does not affect payload shapes.

### Provisioner-side concurrency

Two events for the same data product can arrive at the provisioner concurrently (e.g. user double-clicks in the UI; two updates in quick succession). Naïve handlers will race on IAM trust policy updates, S3 grants, and similar shared infrastructure.

Recommended provisioner pattern: serialise event handling per root entity (data product / exploration / output port). An in-memory queue or per-entity lock is enough in most cases. The portal does not enforce this; it is documented guidance for provisioner authors.

### Handler idempotency

Provisioner handlers should treat each event as "ensure the downstream system reflects this state" rather than "apply this delta". Before adding a principal to a trust policy, check whether it is already present. Before granting access, check whether the grant already exists. This makes duplicate deliveries, replays, and concurrent handlers safe by construction, and it is a hard requirement once cascade events (Option 6) are in play.

### Future: service-emitted events

Today, events are emitted from the router layer. A future refactor will move event emission into the service layer so that any code path that mutates an entity — including direct service-to-service calls — produces the right events. This is acknowledged as in-flight architectural work; it is not gated by this ADR but is the natural place for the cascade emission of Option 6 to live.

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
- **Good, because** `output_port.link_approved` and `technical_asset.linked` can embed both sides (requesting DP + output port + relevant TAs + existing consumers), eliminating round-trips on the hot path.
- **Good, because** branching state (link status APPROVED vs PENDING, TA status transitions) can be carried explicitly on the event.
- **Good, because** combined with Option 6 it solves cascading deletes without forcing fat delete payloads.
- **Neutral, because** requires upfront scoping of each event (see Appendix A) and a worked use case to validate the scope.
- **Bad, because** two model hierarchies (API responses + event payloads) must be maintained in parallel; care is needed to keep them from drifting back into coupling.
- **Bad, because** payloads might still not include what a specific provisioner needs in every flow; SDK hydration remains the fallback for non-delete cases.

### Option 4: ID-only events + finalizers (Kubernetes-style)

- **Good, because** the event contract stays tiny — only IDs travel on the wire.
- **Good, because** the delete-cascade problem dissolves cleanly: deletes are explicitly blocked until every provisioner signs off, so nothing is gone before teardown finishes.
- **Good, because** the pattern is well understood from Kubernetes; provisioners that already think in terms of controllers map onto it directly.
- **Bad, because** portal deletes become asynchronous and block on external systems, changing the UX contract of every delete affordance in the product.
- **Bad, because** events still need SDK round-trips; the finalizer trick only addresses delete semantics.
- **Bad, because** moving from fire-and-forget events to two-phase-commit deletes is a much larger architectural shift than this ADR is scoped to make.

### Option 5: Provisioner-side state tracking

- **Good, because** every provisioner must already track what it has provisioned in order to remove it cleanly; making this explicit improves teardown and migration robustness regardless of what the portal sends.
- **Good, because** it provides a safety net independent of the event contract — a provisioner can reconcile against its own state if portal events are missed or mis-delivered.
- **Neutral, because** this is provisioner-side guidance rather than a portal decision; it affects documentation, not the portal's event design.
- **Bad, because** it adds operational burden to every provisioner implementation.

### Option 6: Cascade event emission

- **Good, because** every cascaded child gets its own delete/unlink event; handlers stay small and focused.
- **Good, because** it keeps individual event payloads minimal — no need to embed lists of children inside a parent's delete event.
- **Good, because** it matches how provisioners actually want to think about teardown: per output port, per technical asset, per link, not per parent.
- **Neutral, because** it requires the portal to fan out events for cascades that today happen silently in the database; emission must happen *before* the DB cascade so that child state is still readable.
- **Bad, because** more events on the wire means more opportunities for ordering or duplication issues; handler idempotency becomes a hard requirement, not a recommendation.

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

The general rule: an event must be self-contained for any branching decision a provisioner needs to make on it. With Option 6 in effect, "cascade" no longer means "embed children in the parent payload" — it means "emit a separate event per child before the DB cascade fires."

| Situation | Include extra state? | Reason |
|---|---|---|
| Create events | No | No prior state, no consumers, nothing to embed. |
| Update / status / settings events on a live object | No | Object still exists; SDK round-trip acceptable. |
| Delete events on a single entity | No (children handled separately) | The portal emits per-child unlink/delete events *before* the DB cascade, so each handler still sees the child state on its own event. |
| Link state transitions (linked / unlinked) | Yes — current link status | Provisioner branches between APPROVED and PENDING; status must be on the event. |
| Status transitions where old state matters | Yes — old + new | E.g. TA PENDING→ACTIVE vs ACTIVE→ARCHIVED have opposite infrastructure effects. |
| Link approval / TA linked | Yes — both sides + existing consumers | A single event must let the provisioner grant access without round-trips. Existing consumers of an output port are not derivable from a TA-link event without an SDK call, so they are embedded. |

### Cascade Emission Order

- **Creates** propagate parent → child: `data_product.created` fires first, then `technical_asset.created` for any default assets, then `output_port.created` events if applicable.
- **Deletes** propagate child → parent. For a data product deletion, this means:
  1. `data_product.input_port_unlinked` for every input port the data product holds.
  2. For each output port: `technical_asset.unlinked` for every TA-OP link, then `data_product.input_port_unlinked` for every consumer's link to that output port, then `output_port.deleted`.
  3. `technical_asset.deleted` for each remaining technical asset.
  4. Finally, `data_product.deleted`.

  Each event fires while its own subject state is still readable, so the carrying payload remains accurate.

### Data Product Events

| Event | Payload | Notes |
|---|---|---|
| `data_product.created` | `DataProductPayload` + `team_members: list[RoleAssignmentPayload]` | Trust policy is populated at creation; the initial owner(s) must arrive on this event, not via follow-up `team_member_added` events. |
| `data_product.updated` | `DataProductPayload` (old + new) | Domain change is the disruptive case; the old domain must be known for migration. |
| `data_product.deleted` | `DataProductPayload` | Cascaded children (output ports, technical assets, input port links) are torn down through their own cascade events. The DP delete event itself only carries the DP. |
| `data_product.about_updated` | `DataProductPayload` | About is fetched via SDK if needed (e.g. by an AI-agent integration that uses it as a system prompt). |
| `data_product.status_updated` | `DataProductPayload` (with new status) | |
| `data_product.setting_changed` | `DataProductPayload` + `setting: SettingPayload` (old + new value) | Provisioner branches on which setting changed and how; shipping the full setting avoids a round-trip on the very next instruction. |
| `data_product.team_member_added` | `DataProductPayload` + `RoleAssignmentPayload` | |
| `data_product.team_member_removed` | `DataProductPayload` + `RoleAssignmentPayload` | |
| `data_product.team_member_updated` | `DataProductPayload` + `RoleAssignmentPayload` (with old + new role) | Role transitions to/from non-integration roles drive trust-policy updates. |
| `data_product.input_port_linked` | `data_product: DataProductPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` + `link_status` (APPROVED / PENDING) | Without `link_status`, the provisioner cannot distinguish unrestricted (act now) from restricted (wait for approval). |
| `data_product.input_port_unlinked` | Same as `linked` + `link_status` at removal time | Also fires as a cascade child when an output port or data product is deleted. Without the status the provisioner cannot tell whether access was ever granted, and therefore whether anything needs revoking. |

`input_port_linked/unlinked` fires on the requesting data product's side. Access grants/revokes for restricted output ports are driven by `output_port.link_approved` / `link_denied`; unrestricted output ports are granted on the link event itself, which is why the link status must be on it.

### Exploration Events

Explorations have no output ports, no technical assets, and no settings; their payloads stay correspondingly small.

| Event | Payload | Notes |
|---|---|---|
| `exploration.created` | `ExplorationPayload` + `owner: RoleAssignmentPayload` | Trust policy needs the owner at creation. |
| `exploration.deleted` | `ExplorationPayload` | Input port unlinks fire as their own cascade events. |
| `exploration.input_port_linked` | `exploration: ExplorationPayload` + `output_port: OutputPortPayload` + `owning_data_product: DataProductPayload` + `link_status` | Mirrors `data_product.input_port_linked`. |
| `exploration.input_port_unlinked` | Same as `linked` + `link_status` at removal time | Mirrors `data_product.input_port_unlinked`. |

### Output Port Events

| Event | Payload | Notes |
|---|---|---|
| `output_port.created` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.updated` | `DataProductPayload` + `OutputPortPayload` | |
| `output_port.deleted` | `DataProductPayload` + `OutputPortPayload` | TA-unlink events and per-consumer input-port-unlink events fire as cascaded children before this. |
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
| `technical_asset.deleted` | `DataProductPayload` + `TechnicalAssetPayload` | Per-OP unlink events fire as cascaded children before this; consumer-level revocation flows through those. |
| `technical_asset.linked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` + `consumers: list[DataProductPayload]` | Existing approved consumers of the OP must receive a grant immediately on this event; they are not derivable from a TA-level event without an SDK call, so they are embedded. |
| `technical_asset.unlinked` | `DataProductPayload` + `OutputPortPayload` + `TechnicalAssetPayload` + `consumers: list[DataProductPayload]` | Existing approved consumers of the OP must have their grant revoked if they have no other path to this TA. Also fires as a cascade child when an output port or technical asset is deleted. |

TA events always include `TechnicalAssetPayload` since the TA carries the platform configuration. `OutputPortPayload` is included only where the event concerns a TA↔OP relationship.
