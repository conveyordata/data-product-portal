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

The catalogue is deliberately small. There are six entities: five of them have `created` / `updated` / `deleted` events, and `technical_asset_link` has only `created` / `deleted` (the link has no updateable state) — seventeen events total. Payloads aim for the 80% of provisioner work; the remaining 20% (rarer flows, display-only fields, deep relationship state) is served by SDK calls against the still-live entity, or by the provisioner maintaining its own cache from prior events.

State-specific transitions that previous drafts modelled as their own events — `setting_changed`, `team_member_added`, `status_updated`, `about_updated`, `link_approved`, `link_denied` — are folded into the relevant entity's `updated` event. Provisioners diff `old` and `new` to discover what changed. This is the Kubernetes-operator reconciliation pattern: a simpler event surface, more provisioner-side logic.

### Entities

1. **`data_product`**
2. **`exploration`**
3. **`output_port`**
4. **`technical_asset`**
5. **`input_port`** — the link between a requester (a data product or an exploration) and an output port. Treated as a first-class entity, with its own lifecycle (`created` when requested, `updated` when the status transitions PENDING → APPROVED, `deleted` when removed), rather than living inside its parents' events.
6. **`technical_asset_link`** — the link between an output port and a technical asset. Treated as a first-class entity for symmetry with `input_port`: the relationship has its own lifecycle, and modelling it directly keeps `output_port.updated` from doubling as a link-event channel. The link itself has no updateable state, so `technical_asset_link` has only `created` and `deleted`.

### Substructures

Used inside the entity payloads.

- **`setting`** — `id`, `name`, `value`
- **`role_assignment`** — `id`, `user_id`, `user_email`, `role`

### Entity payloads

Every event for a given entity carries the same payload shape: `created` and `deleted` carry one copy, `updated` carries `old` and `new`.

#### `data_product`

- `id`, `name`, `namespace`
- `domain_id`, `domain_name`
- `type_id`, `type_name`
- `lifecycle_name` (nullable), `status`
- `settings: list[setting]`
- `team_members: list[role_assignment]`

#### `exploration`

- `id`, `name`, `namespace`, `status`
- `owner: role_assignment`

#### `output_port`

- `id`, `name`, `namespace`
- `data_product_id`
- `access_type` (`restricted` / `unrestricted`), `status`
- `settings: list[setting]`
- `team_members: list[role_assignment]`

The OP does not carry a list of its linked technical assets. That relationship lives in the `technical_asset_link` entity; provisioners reconstruct per-OP TA lists from `technical_asset_link` events.

#### `technical_asset`

- `id`, `name`, `namespace`
- `platform_id`, `service_id`
- `configuration`, `status`, `mapping` (default / custom)
- `data_product_id`

#### `input_port`

- `id`, `status` (`PENDING` / `APPROVED`)
- `requester`: discriminated reference object — `type` (`data_product` or `exploration`), `id`, `name`, `namespace`
- `output_port`: reference object — `id`, `name`, `namespace`, `data_product_id`

The requester carries `namespace` directly because that is the identifier the consumer-side provisioner uses to address the resource it grants access on (e.g., the IAM role `dpp-{namespace}` in the AWS S3 use case). Full requester and output-port state — including which TAs are behind the output port — is read from the provisioner's caches of `data_product` / `exploration` / `output_port` / `technical_asset` / `technical_asset_link` events.

#### `technical_asset_link`

- `id`
- `output_port`: reference object — `id`, `name`, `namespace`, `data_product_id`
- `technical_asset`: reference object — `id`, `name`, `namespace`

Carries no state of its own beyond the two references. Only `created` and `deleted` events fire.

### Event semantics

The five primary entities each have three events; `technical_asset_link` has two.

- **`<entity>.created`** — carries the entity payload. Fires when the entity comes into existence.
- **`<entity>.updated`** — carries `old: <entity>` and `new: <entity>`. Fires for any change to the payload fields. Provisioners diff old vs. new to find what changed (status, settings, team members, link status, …). Not defined for `technical_asset_link`, which has no updateable state.
- **`<entity>.deleted`** — carries the entity payload as it was just before deletion. Fires after the cascade children (see below). Final state for tear-down.

Seventeen events total: 5 entities × 3 events, plus `technical_asset_link.created` and `technical_asset_link.deleted`.

Folding examples:

| Was, in earlier drafts | Now |
|---|---|
| `data_product.setting_changed` | `data_product.updated` with `new.settings ≠ old.settings` |
| `data_product.about_updated` | not on the event surface; provisioners SDK-fetch `about` |
| `data_product.status_updated` | `data_product.updated` with `new.status ≠ old.status` |
| `data_product.team_member_added` / `_removed` / `_updated` | `data_product.updated` with a changed `team_members` list |
| `data_product.input_port_linked` / `_unlinked` | `input_port.created` / `input_port.deleted` |
| `output_port.link_approved` / `link_denied` | `input_port.updated` (PENDING → APPROVED) / `input_port.deleted` while PENDING |
| `technical_asset.linked` / `_unlinked` | `technical_asset_link.created` / `technical_asset_link.deleted` |
| `technical_asset.status_updated` | `technical_asset.updated` with `new.status ≠ old.status` |

### Cascade Emission Order

When a parent is deleted, the portal emits per-child events *before* the database cascade commits, so each child event still carries readable state.

- **`exploration.deleted`** → `input_port.deleted` for every input port owned by the exploration, then `exploration.deleted`.
- **`output_port.deleted`** → `input_port.deleted` for every input port pointing at the output port, `technical_asset_link.deleted` for every link involving the output port, then `output_port.deleted`. The TAs themselves survive (they belong to the data product).
- **`technical_asset.deleted`** (standalone — not as a cascade child of a data product delete) → `technical_asset_link.deleted` for every link involving this TA, then `technical_asset.deleted`.
- **`data_product.deleted`** →
  1. `input_port.deleted` for every input port owned by the data product.
  2. For each output port owned by the data product: `input_port.deleted` for every consumer pointing at it, `technical_asset_link.deleted` for every TA linked to it, then `output_port.deleted`.
  3. `technical_asset.deleted` for each technical asset owned by the data product. Same-DP assumption: `technical_asset_link` rows for these TAs were already cleared in step 2; cross-DP linking, if introduced later, would require cascading `technical_asset_link.deleted` here too.
  4. `data_product.deleted`.
- **`input_port.deleted`** and **`technical_asset_link.deleted`** are terminal (no children).

### What the 80/20 leaves to the SDK

Fields and relationships intentionally not on events; the provisioner SDK-fetches when needed:

- Display-only fields: `about`, `tags`, descriptions.
- Full state of an entity referenced from another entity (e.g., the `output_port` and `technical_asset` references on `technical_asset_link`, or the `requester` and `output_port` references on `input_port`, carry only minimal identifying fields; the provisioner reads underlying state from caches built from the referenced entities' own `created` / `updated` / `deleted` events, or SDK-fetches on cold start).
- Anything else a specific provisioner needs. If a use case shows a field is hot-path-critical, the catalogue can grow via a follow-up ADR.

---

## Appendix B: Implementation Plan

The work breaks into a small set of additive tasks followed by per-entity migration that can run in parallel.

### Tasks and dependencies

```
T1 ─► T2 ─► T3 (SDK export)
       │
       └─► T6.x (per-entity wiring)
                ▲
T4 ─► T5 ──────┘
```

**T1 — Define substructures and entity payloads.** No dependencies.
- Create Pydantic models under `backend/app/core/webhooks/` for the two substructures (`setting`, `role_assignment`) and the six entity payloads (`data_product`, `exploration`, `output_port`, `technical_asset`, `input_port`, `technical_asset_link`) per Appendix A.
- Pure addition. No existing code consumes the new models yet.

**T2 — Define CRUD event types.** Depends on T1.
- For each of the five primary entities, define three event types: `<entity>.created`, `<entity>.updated`, `<entity>.deleted`. `created` and `deleted` carry the entity payload directly; `updated` carries `old` and `new` of it.
- For `technical_asset_link`, define only `technical_asset_link.created` and `technical_asset_link.deleted` (the link has no updateable state).
- Seventeen events total.
- Still no consumers; existing `V2Event` subclasses are not yet rewired.

**T3 — SDK export and documentation refresh.** Depends on T2. Runs in parallel with T4–T6.
- Export the new payload and event models from the Python SDK.
- Remove the auto-generated documentation that was previously emitted for V2 events; replace with hand-curated entries that match the new catalogue.

**T4 — Decide event emission architecture.** No dependencies. Runs in parallel with T1–T3.
- Short spike + decision note. Two candidate approaches:
  - **A — Keep emission in routers, add a collector service.** A new service is responsible, given a mutation, for returning the full list of events to dispatch (parent + cascade children, in the right order). Routers call the collector and dispatch what comes back. Lower blast radius; matches today's architecture.
  - **B — Remove DB cascade deletes; move emission into services.** Services own their entity's lifecycle and emit events directly; cascades become explicit service-to-service calls. Aligns with the hexagonal direction noted in *Related Operational Concerns*, but is significantly more code.
- Output: a follow-up note in this ADR (or a sibling ADR) recording the choice. Either approach is compatible with the payloads above.

**T5 — Wire cascade emission plumbing.** Depends on T4.
- Implement the chosen approach's mechanics: on a parent delete, iterate children and fire their events *before* the database cascade commits.
- Adds the per-child events to the dispatch path but does not yet change individual event payloads — those flip in T6.x.

**T6.x — Per-entity migration (parallelizable).** Depends on T2 and T5. Six tasks, one per entity (data_product / exploration / output_port / technical_asset / input_port / technical_asset_link). Each task:
1. Switches the dispatch sites for that entity's `created`, `updated`, `deleted` to the new payload models.
2. Removes any of the now-obsolete state-specific events for that entity (`setting_changed`, `team_member_added`, `status_updated`, `about_updated`, `link_approved`, `link_denied`, `technical_asset.linked`, etc.); those signals are now expressed by the entity's `updated` event.
3. Updates integration tests and fixtures tied to the old shape.

Splitting per-entity lets each migration land independently. They touch different services / routers; the only shared state is the dispatcher itself.

### Coordinating breaking changes with other contributors

Switching to the new payloads is a breaking change on the wire for every event. Inside the codebase, the change is local — one entity at a time. Two concerns to mitigate:

1. **Mid-flight churn for other contributors.** While T6.x rolls out, new feature work that touches event emission could pick the wrong pattern. Mitigation:
    - Merge T1–T3 quickly and announce that all new V2 event work uses the new payload models from that point on.
    - Mark the old `V2Event` subclasses as deprecated in code so unmigrated callers fail review.

2. **External consumers seeing inconsistent payloads.** The V2 webhook contract is in early adopter status; some breakage is acceptable, but it should be visible. Mitigation, in order of preference:
    - **(Preferred) Treat V2 as in-development**, document the catalogue as the canonical shape, and roll forward entity by entity. Communicate the change window to early adopters.
    - **(Fallback) Bump to V3** if breakage of an in-flight V2 consumer would be costly. Run V2 and V3 dispatchers side by side until V2 can be retired.
    - **(Last resort) Feature-flag the new payload shape** per environment. Avoid this if possible — it doubles the test matrix.

The expectation is the first option. T6.x then proceeds incrementally without parallel-event-format scaffolding.
