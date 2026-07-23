# Split Input Ports into a Link and Access Requests

## Context and Problem Statement

Time-bound access to output ports is currently modelled on a single `input_ports` table. That table conflates two concepts: the **relationship** (a consumer consumes an output port) and the **access request/grant lifecycle** (who requested, who decided, when it expires). As a result it is hard to keep an auditing log of renewals and denials, and the state of the read access is mixed with the state of the request.

The current implementation uses an `EXPIRED` status flipped by a background task, an `is_renewing` boolean, `total_range_start/end` bookkeeping, and renewal logic that *mutates the existing grant row in place*, losing history. Edge cases such as "access is still valid, a renewal was requested and then denied" cannot be represented cleanly. The upcoming feature to allow a justification on a denied access request is also not possible in the current model.

Expiry cannot be purely computed: the provisioner keeps the infrastructure state in sync from **events**, and it only reacts when it receives one. If a grant simply lapsed without an event, the provisioner would never revoke the infra access. So a background task is still required to detect expiry and emit the access-ended event, and we need a way to guarantee that event is delivered.

**Core question: how should the access relationship, its request/decision history, and the current grant be modelled?**

## Decision Drivers

* Auditability — keep a history of requests, renewals and denials instead of overwriting one row
* Renewals without losing history — a renewal must not mutate the previous grant
* Support a denial justification (upcoming feature)
* Separate the *relationship* from the *request/decision* from the *grant* (a time-bounded window)
* Keep the infrastructure in sync — the provisioner is event-driven, so expiry must emit an event (a background task stays), with a delivery guarantee
* Reduce the complexity and risk of the current renewal/expiry logic (in-place mutation, `is_renewing`)
* Minimise refactoring and stay backward-compatible for already-released clients (frontend, published SDK, Go CLI)

## Considered Options

* **Option 1: Keep the single `input_ports` table** — extend it with more flags and dates to cover renewals, denials and expiry.
* **Option 2: Split into `input_ports` (link) + `input_port_requests`** — a lightweight link that carries the current access state, plus one row per access request/grant.

This mirrors how identity-governance systems (e.g. Entra PIM, Google Cloud IAM) model access: separate the relationship, the request/decision (an append-only audit trail), and the grant (a time-bounded window).

## Decision Outcome

**Chosen option: Option 2 — split into `input_ports` and `input_port_requests`.**

The link keeps identity plus a `status` that expresses the current access state (`PENDING / APPROVED / DENIED / EXPIRED / REVOKED / CANCELLED`). Every request or renewal is a new row in `input_port_requests`; approving, denying, revoking and cancelling all decide or annotate an existing row rather than mutating a grant in place, so history is preserved and every transition is auditable. A request's own `decision` is `PENDING / APPROVED / DENIED / CANCELLED`; an `APPROVED` request additionally carries `revoked_at` / `revoked_by_id` once access is revoked.

The background task is retained but simplified: a **daily** job (also run on application startup) flips a lapsed grant's link to `EXPIRED` and emits the access-ended event to the provisioner. `is_renewing` and the in-place renewal mutation are removed. `is_expiring_soon` is computed in the backend for the UI.

### Confirmation

* A new `input_port_requests` table exists; `input_ports` keeps only identity and the access-state `status`.
* Requesting access, renewing, approving, denying, revoking and cancelling create, decide or annotate request rows, not mutate a grant in place.
* The link `status` additionally carries `REVOKED` and `CANCELLED`; the request `decision` gets its own `CANCELLED` value but never `EXPIRED` or `REVOKED` — those are link-only, and revocation is instead tracked by `revoked_at` / `revoked_by_id` on an `APPROVED` request.
* The UI has no delete action for an input port or a request; revoke and cancel are the only ways to end access there, and both preserve the link and its full request history. A backend-only hard-delete route stays on each side as a two-way door (see Revoking and cancelling).
* The background task is retained (daily + on startup) to set `EXPIRED` and emit the access-ended event, with a delivery-guarantee marker. `is_renewing` is removed.
* A migration backfills one request per existing link and moves the request columns off the link.
* A `GET /input_ports/{id}/requests` endpoint lists a link's request history.

## Pros and Cons of the Options

### Option 1: Keep the single table

* **Good, because** no schema split and no migration of existing rows.
* **Neutral, because** it keeps the model familiar to the current code.
* **Bad, because** renewals overwrite the grant in place, so there is no history.
* **Bad, because** denials and renewals cannot be audited, and a denial justification cannot be added.
* **Bad, because** it keeps the `is_renewing` flag and the fragile in-place renewal logic.
* **Bad, because** without an audit trail, bugs are easy to introduce and hard to diagnose.

### Option 2: Split into link + requests

* **Good, because** every request/renewal/denial is its own row — full history and audit trail.
* **Good, because** an active grant can coexist with a pending or denied renewal.
* **Good, because** it removes `is_renewing` and the in-place mutation, simplifying the renewal flow and the background task.
* **Good, because** a denial justification fits naturally on the request row.
* **Good, because** with an audit trail, bugs are easier to diagnose, reducing the mental burden for everyone.
* **Neutral, because** the background task is still needed for the provisioner (expiry events).
* **Bad, because** it requires a new table and a one-time backfill migration.

## Design Details

### `input_ports` — the link (output port ↔ consumer)

Keep:

| Column | Meaning |
| --- | --- |
| `id` | PK |
| `dataset_id` → datasets | the output port |
| `consuming_abstract_data_product_id` → abstract_data_products | the consuming data product / exploration |
| `status` | `PENDING / APPROVED / DENIED / EXPIRED / REVOKED / CANCELLED` — the current access state (see Link status). Reused from today; the daily job maintains `EXPIRED`, and `recompute_status` maintains `REVOKED` / `CANCELLED` after a revoke or cancel. |
| `created_by` | the consumer-side owner to notify for renewals |
| `created_on`, `updated_on` | audit |

Add:

| Add | Meaning |
| --- | --- |
| `expiry_event_sent` | marks that the access-ended event has been dispatched to the provisioner, so the daily job / startup can re-send it if it was missed |

Remove (moved to `input_port_requests`, or dropped):

| Removed column | What happens to it |
| --- | --- |
| `justification` | moved to the request, can be copied over for renewals (each request has its own reason; also allows a denial justification later) |
| `requested_on`, `requested_by_id` | moved to the request |
| `approved_on`, `approved_by_id` | moved to the request as `decided_on` / `decided_by_id` |
| `denied_on`, `denied_by_id` | moved to the request as `decided_on` / `decided_by_id` |
| `renewed_on`, `renewed_by_id` | dropped — a renewal is its own request; its `decided_on` / `decided_by` is the "renewed by/on" |
| `is_renewing` | dropped — a renewal in flight is a PENDING request on the link |
| `expired_on` | dropped — the grant's end is the request's `valid_until`; the link's `EXPIRED` status marks it |
| `expires_on` | moved to the request as `valid_until` |
| `total_range_start` | moved to the request as `valid_from` |
| `total_range_end` | dropped — same value as `valid_until`; the overall span is derived from the request history |
| `requested_duration_days` | moved to the request |

### `input_port_requests` — the new table (one row per request)

Requests reference the link one-directionally via `input_port_id`; the link holds no request list. The UI never deletes a request or its link — see Ending access.

| Column | Meaning |
| --- | --- |
| `id` | PK |
| `input_port_id` → input_ports | the link this request belongs to |
| `decision` | `PENDING / APPROVED / DENIED / CANCELLED` — its own `InputPortRequestDecision` enum, kept separate from the shared `DecisionStatus` used by other approval flows |
| `justification` | the consumer's reason for this request; on a renewal the previous request's justification is reused |
| `access_duration_type` | `PERMANENT` or `TIME_BOUND` — stored on the request (also derivable from `valid_until` / `requested_duration_days`, but kept for clarity) |
| `requested_duration_days` (nullable) | requested window length; NULL = permanent |
| `requested_on`, `requested_by_id` → users | when / who requested |
| `decided_on` (nullable), `decided_by_id` (nullable) → users | when / who approved, denied or cancelled (which one is told by `decision`) |
| `revoked_at` (nullable), `revoked_by_id` (nullable) → users | when / who revoked an approved grant; only ever set on a request whose `decision` is `APPROVED` |
| `valid_from` (nullable, date) | start of the granted window (set at approval) |
| `valid_until` (nullable, date) | last day of the granted window, **inclusive**; NULL = permanent |
| `created_on`, `updated_on` | audit |

`valid_from` / `valid_until` are dates (day granularity, no time-of-day); `valid_until` is inclusive — access is valid through that day.

`access_duration_type` and `requested_duration_days` are set when the request is created, from the output port's access-duration policy for the consuming type (the admin default configured for a data product or an exploration). `valid_from` and `valid_until` are set when the request is approved.

Constraint: at most one PENDING request per link (partial unique index). A new request is allowed at any time as long as none is currently pending.

### Link status

The link `status` uses a six-value enum (`PENDING / APPROVED / DENIED / EXPIRED / REVOKED / CANCELLED`); the request `decision` uses its own four-value `InputPortRequestDecision` (`PENDING / APPROVED / DENIED / CANCELLED`). `status` is a stored column, but it is written in only one place: a `recompute_status` method that derives it from the request rows and runs after every request change (the daily job runs the same logic for the `EXPIRED` transition).

A pending request never eclipses a real prior outcome on its own, a renewal submitted after a grant expired, was revoked, or was denied keeps showing that prior outcome (with `renewal_status`/the UI's "Renewal pending" tag signalling that something is in flight), rather than collapsing the link back to `PENDING`. `PENDING` is reserved for when there's genuinely nothing else to show: a first-ever request, or a fresh request after a denial that was never actually approved — in both cases nothing else on the link signals that a decision is awaited, so `status` has to. Concretely, `recompute_status` resolves the state in this order, using the active grant (the single approved request whose window covers today and which has not been revoked), the pending request (the request whose `decision` is still `PENDING`), and whether the link was *ever* approved (any request, ever, with `decision = APPROVED`):

1. **APPROVED** — there is an active grant. The consumer has access. A pending, denied or cancelled renewal does not change this.
2. **PENDING** — there is a pending request, and the link was never approved before (a first-ever request, or a fresh request after a plain denial). Nothing else would indicate this request is awaiting a decision, so `status` must.
3. Otherwise (no active grant, and either no pending request, or a pending request sitting on top of a link that *was* approved at some point — a real renewal, where `renewal_status` already signals it's in flight) — skip past any cancelled or pending request and take the most recent request that ever received a real decision (`APPROVED` or `DENIED`):
   - **CANCELLED** — no such request exists at all; every request ever made on this link was cancelled before a decision.
   - **REVOKED** — that request was `APPROVED` with `revoked_at` set.
   - **EXPIRED** — that request was `APPROVED` with `revoked_at` unset (the window simply passed). Set by the daily job.
   - **DENIED** — that request was `DENIED`.

`current_request` (the request whose `justification` / `valid_until` / `decision_note` the UI shows) mirrors this exact resolution, so the fields displayed always belong to whichever request `status` was actually derived from, a cancelled or pending renewal never becomes "current" over the grant it was renewing.

When a renewal is approved while a grant is still active, its window starts the day after the current grant's `valid_until`, so at most one grant covers any given day and no existing grant is modified. If the previous grant has already lapsed or been revoked, the new window starts today.

### Revoking and cancelling

The UI only ever offers revoke and cancel — never a delete. Ending access this way never deletes anything: the link and its full request history stay.

* **Revoke** ends an active grant. Either the producer (the output port owner, pulling a consumer's access) or the consumer (giving up their own access) can revoke it. It sets `revoked_at` / `revoked_by_id` on the active grant's request; the request's `decision` stays `APPROVED` — it really was approved, and revocation is a separate, later fact layered on top, the same way `decided_on` / `decided_by` already work. No reason is stored; a confirmation dialog is the only safeguard against an accidental click.
* **Cancel** withdraws a request that is still `PENDING`, before anyone decided it. Only the consumer who made the request can cancel it. It sets the request's `decision` to `CANCELLED` and its `decided_by` / `decided_on` — the same columns `approve` and `deny` already use, since a cancelled request was never decided by the producer but did reach a final state of its own. Because a cancelled request's `decision` is no longer `PENDING`, the "one pending request per link" constraint does not block a fresh request afterward.
* **Deny** only ever acts on a `PENDING` request; it cannot act on an active grant — ending an active grant is revoke's job.

Both backend routers additionally keep a hard-delete route alive — `POST .../input_ports/remove` on the producer side, `DELETE .../input_ports/{output_port_id}` on the consumer side — deleting the link and cascading its requests, exactly as before this feature existed. Neither is wired to any frontend button. They stay as a two-way door: if fully removing an input port (not just ending its access) ever turns out to be genuinely needed, the capability already exists rather than having to be rebuilt; if it never is, the only cost was keeping an unused route around.

### Expiry background task

The provisioner reacts to events, so expiry is handled by a job rather than computed silently:

* Runs **daily** (day granularity — expiry is checked against the date, not the hour) and **on application startup**, so a missed day (e.g. the app was down) is caught on the next run.
* For each link whose effective grant window has passed and whose access-ended event has not yet been sent: emit the access-ended event (the provisioner revokes infra), set the link `status` to `EXPIRED` when no request is pending (otherwise leave it `PENDING`), and set `expiry_event_sent`.
* `expiry_event_sent` is the delivery guarantee: if emitting the event fails, the next daily run or startup retries it. The same marker is reset when a new grant is approved so a later expiry fires again.

### Computed fields (for the UI)

As agreed in the meeting, the background task owns the state logic; a couple of convenience fields are exposed for easy UI rendering. They are computed (not persisted). If querying or consistency ever needs it, they could instead be columns on `input_ports` maintained by the background task.

* `is_expiring_soon` — an approved grant is within the expiring-soon threshold of `valid_until`. Drives the renew button and warning banner.
* `is_renewing` — the link has an active grant and a renewal request is currently PENDING. Lets the UI show a "renewing" state.

### Endpoint changes

All paths stay on `/api/v2`; changes are additive.

**Consumer side** (a data product or exploration managing what it consumes):

* `GET /data_products/{id}/input_ports` and `GET /explorations/{id}/input_ports` — list a consumer's input ports. Response adds `is_expiring_soon` and the effective end date (`valid_until`); the link `status` now includes `EXPIRED`; grant fields come from the active request.
* `GET /input_ports/{id}/requests` — list all requests for a given input port (the audit/history view).
* `POST /data_products/{id}/input_ports` and `POST /explorations/{id}/input_ports` — request access; also the single entry point for renewal. If a link already exists for that (consumer, output port), it adds a new request instead of failing as "already exists" or mutating the old grant; on a renewal the previous justification is reused. Blocked if a request is already PENDING on the link, or if the current active grant is permanent (`valid_until = NULL`) — permanent access never lapses, so there is nothing to renew, unless it is first revoked (see Ending access).
* `POST /data_products/{id}/input_ports/{output_port_id}/cancel` (and exploration equivalent) — withdraw a still-pending request.
* `POST /data_products/{id}/input_ports/{output_port_id}/revoke` (and exploration equivalent) — give up an active grant.

**Producer side** (an output port owner managing consumers):

* `GET /data_products/{dp}/output_ports/{op}/input_ports` — list the consumers of an output port; same additive response changes.
* `POST .../input_ports/approve` — decide the link's single PENDING request; sets `decided_by/on`, and sets `valid_from/valid_until` from the requested duration.
* `POST .../input_ports/deny` — decide the link's single PENDING request; sets `decided_by/on`. Only ever acts on a PENDING request, never on an active grant.
* `POST .../input_ports/renew` — producer-initiated extension; adds a new APPROVED request (`decided_by` = the producer) rather than overwriting the current grant's dates.
* `POST .../input_ports/revoke` — end an active grant; the link and its request history stay.

**Approver queue:**

* `GET /users/current/pending_actions` — includes pending input-port requests. The item sources its who/when/duration fields from the request and adds `decided_by`; `approved_by` / `denied_by` are kept as deprecated aliases (from `decided_by`) for one release.

### Ending access

The UI never deletes an input port or a request. Revoke and cancel (see Revoking and cancelling) are the only ways to end access or withdraw a request there, and both keep the link and its full request history — a backend-only hard-delete route stays on each side as a two-way door, not wired to any button. Changing a permanent grant to time-bound (or back) in place is not possible; it is revoked first, freeing the link up for a fresh request or renewal.

### Edge cases and outcomes

| # | Scenario | Outcome |
| --- | --- | --- |
| 1 | Unrestricted OP, permanent | Request auto-approved, `valid_until=NULL` → link APPROVED, no expiry |
| 2 | Unrestricted OP, time-bound | Auto-approved, `valid_from=today`, `valid_until=today+days` → APPROVED until the window passes |
| 3 | Restricted OP, time-bound, request | Request PENDING (`requested_duration_days` set) → link PENDING; on approve → `valid_from/until` set, link APPROVED |
| 4 | Restricted OP request denied | Request DENIED; link stays, shown as DENIED |
| 5 | Re-request after denial | New request on the same link — no duplicate link |
| 6 | Active grant + renewal denied | Link stays APPROVED; the denied renewal is visible in the request history |
| 7 | Active grant + renewal approved | New approved request with a later `valid_until`; the earlier grant becomes historical |
| 8 | Renewal after expiry | Grant lapsed → daily job emits access-ended event and sets link EXPIRED; renewal request → link PENDING; approve → APPROVED + event |
| 9 | Expiring soon | Backend computes `is_expiring_soon` from `valid_until`; UI shows renew button + warning; no state change |
| 10 | Permanent grant | `valid_until=NULL` → APPROVED, no expiry, no extend |
| 11 | Producer extend | Producer adds a new approved request (`decided_by` = producer) |
| 12 | Second request while one pending | Blocked (one pending per link) → 400; DB partial-unique-index backstop |
| 12b | New request while the current grant is permanent | Blocked → 400; permanent access has nothing to renew. To re-scope it to time-bound, revoke it first, then request or renew |
| 13 | Consumer gives up an active grant | Consumer revokes → request `decision` stays APPROVED, `revoked_at` / `revoked_by_id` set → link REVOKED |
| 13b | Producer pulls a consumer's active grant | Producer revokes → same as above; either side can end an active grant |
| 13c | Consumer withdraws a pending request | Consumer cancels → request `decision` → CANCELLED, `decided_by/on` set → link CANCELLED; a new request can be made immediately |
| 14 | Grant lapses while renewal still pending | Daily job emits the access-ended event (infra revoked); link `status` is PENDING until re-approval |

### Backward compatibility

The released contract is the committed OpenAPI spec, and pre-commit regenerates and gate-checks it together with the frontend client, the published Python SDK and the Go CLI. Fields that exist only on the unreleased feature branch (`is_renewing`, `renewed_on`, `renewed_by`, `expired_on`, `total_range_start/end`) are dropped freely. `approved_by` / `denied_by` are released via the pending-actions endpoint, so they are kept as deprecated aliases derived from `decided_by` for one release, then removed with a breaking-changes note. Endpoint paths are unchanged and additive (plus the new `GET /input_ports/{id}/requests`, `.../cancel` and `.../revoke`); the producer-side `.../input_ports/remove` and the consumer-side `DELETE .../input_ports/{output_port_id}` stay too, just no longer referenced by any frontend button (see Revoking and cancelling).

The link `status` keeps `EXPIRED`, and now also `REVOKED` and `CANCELLED`. Released clients validate the status enum against `approved/pending/denied`, so surfacing any of these needs a release-notes entry (or a dedicated link-status enum) rather than a silent enum change.
