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

The link keeps identity plus a `status` that expresses the current access state (`PENDING / APPROVED / DENIED / EXPIRED`). Every request or renewal is a new row in `input_port_requests`, whose own `status` is `PENDING / APPROVED / DENIED` (no `EXPIRED`), so history is preserved and denials/renewals are auditable.

The background task is retained but simplified: a **daily** job (also run on application startup) flips a lapsed grant's link to `EXPIRED` and emits the access-ended event to the provisioner. `is_renewing` and the in-place renewal mutation are removed. `is_expiring_soon` is computed in the backend for the UI.

### Confirmation

* A new `input_port_requests` table exists; `input_ports` keeps only identity and the access-state `status`.
* Requesting access, renewing, approving, denying and revoking create or decide request rows, not mutate a grant in place.
* The link `status` keeps `EXPIRED`; the request `status` does not.
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
| `status` | `PENDING / APPROVED / DENIED / EXPIRED` — the current access state (see Link status). Reused from today; the daily job maintains `EXPIRED`. |
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

Requests reference the link one-directionally via `input_port_id`; the link holds no request list. Deleting a link cascades its requests (see Deletion).

| Column | Meaning |
| --- | --- |
| `id` | PK |
| `input_port_id` → input_ports | the link this request belongs to |
| `status` | `PENDING / APPROVED / DENIED` |
| `justification` | the consumer's reason for this request; on a renewal the previous request's justification is reused |
| `requested_duration_days` (nullable) | requested window length; NULL = permanent |
| `requested_on`, `requested_by_id` → users | when / who requested |
| `decided_on` (nullable), `decided_by_id` (nullable) → users | when / who approved or denied (which one is told by `status`) |
| `valid_from` (nullable, date) | start of the granted window (set at approval) |
| `valid_until` (nullable, date) | last day of the granted window, **inclusive**; NULL = permanent |
| `created_on`, `updated_on` | audit |

`valid_from` / `valid_until` are dates (day granularity, no time-of-day); `valid_until` is inclusive — access is valid through that day.

Constraint: at most one PENDING request per link (partial unique index). A new request is allowed at any time as long as none is currently pending.

### Link status

The link `status` uses a four-value enum (`PENDING / APPROVED / DENIED / EXPIRED`); the request `status` uses the three-value `DecisionStatus`. The link status expresses the **current access state**, resolved in this order:

1. **APPROVED** — an approved request's window still includes today (`valid_until ≥ today`, or NULL for permanent). The consumer has access. A pending or denied renewal does not change this.
2. **PENDING** — there is no currently-valid grant and there is a pending request (a first request, or a renewal after the grant lapsed).
3. **EXPIRED** — there is no currently-valid grant and no pending request, but a prior grant was approved and its window has passed. Set by the daily job.
4. **DENIED** — the latest decided request was denied, and no pending request.

So an active grant with a pending renewal reads `APPROVED`; once that grant lapses while the renewal is still pending it reads `PENDING`.

### Expiry background task

The provisioner reacts to events, so expiry is handled by a job rather than computed silently:

* Runs **daily** (day granularity — expiry is checked against the date, not the hour) and **on application startup**, so a missed day (e.g. the app was down) is caught on the next run.
* For each link whose effective grant window has passed and whose access-ended event has not yet been sent: emit the access-ended event (the provisioner revokes infra), set the link `status` to `EXPIRED` when no request is pending (otherwise leave it `PENDING`), and set `expiry_event_sent`.
* `expiry_event_sent` is the delivery guarantee: if emitting the event fails, the next daily run or startup retries it. The same marker is reset when a new grant is approved so a later expiry fires again.

### Other computed field

* `is_expiring_soon` — computed in the backend from `valid_until` and returned by the API; drives the renew button and warning banner. Not a status and not persisted.

### Endpoint changes

All paths stay on `/api/v2`; changes are additive.

**Consumer side** (a data product or exploration managing what it consumes):

* `GET /data_products/{id}/input_ports` and `GET /explorations/{id}/input_ports` — list a consumer's input ports. Response adds `is_expiring_soon` and the effective end date (`valid_until`); the link `status` now includes `EXPIRED`; grant fields come from the active request.
* `GET /input_ports/{id}/requests` — list all requests for a given input port (the audit/history view).
* `POST /data_products/{id}/input_ports` and `POST /explorations/{id}/input_ports` — request access; also the single entry point for renewal. If a link already exists for that (consumer, output port), it adds a new request instead of failing as "already exists" or mutating the old grant; on a renewal the previous justification is reused. Blocked only if a request is already PENDING on that link.
* `DELETE /data_products/{id}/input_ports/{output_port_id}` (and exploration equivalent) — unlink.

**Producer side** (an output port owner managing consumers):

* `GET /data_products/{dp}/output_ports/{op}/input_ports` — list the consumers of an output port; same additive response changes.
* `POST .../input_ports/approve` and `POST .../input_ports/deny` — decide the link's single PENDING request; sets the request `status` and `decided_by/on`, and on approve sets `valid_from/valid_until` from the requested duration.
* `POST .../input_ports/renew` — producer-initiated extension; adds a new APPROVED request (`decided_by` = the producer) rather than overwriting the current grant's dates.
* `POST .../input_ports/remove` — revoke; deletes the link.

**Approver queue:**

* `GET /users/current/pending_actions` — includes pending input-port requests. The item sources its who/when/duration fields from the request and adds `decided_by`; `approved_by` / `denied_by` are kept as deprecated aliases (from `decided_by`) for one release.

### Deletion

Deleting an input port stays, and for now it cascades its requests. A later iteration may replace hard delete with **cancellation** — keeping the link and its full request history for audit instead of removing it.

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
| 13 | Remove / unlink | Delete the link, cascading its requests (a future iteration may cancel instead, to keep the audit trail) |
| 14 | Grant lapses while renewal still pending | Daily job emits the access-ended event (infra revoked); link `status` is PENDING until re-approval |

### Backward compatibility

The released contract is the committed OpenAPI spec, and pre-commit regenerates and gate-checks it together with the frontend client, the published Python SDK and the Go CLI. Fields that exist only on the unreleased feature branch (`is_renewing`, `renewed_on`, `renewed_by`, `expired_on`, `total_range_start/end`) are dropped freely. `approved_by` / `denied_by` are released via the pending-actions endpoint, so they are kept as deprecated aliases derived from `decided_by` for one release, then removed with a breaking-changes note. Endpoint paths are unchanged and additive (plus the new `GET /input_ports/{id}/requests`).

The link `status` keeps `EXPIRED`. Released clients validate the status enum against `approved/pending/denied`, so surfacing `EXPIRED` on the link needs a release-notes entry (or a dedicated link-status enum) rather than a silent enum change.

## Open Questions

* **Cancellation instead of delete?** Replacing hard delete with cancellation would preserve the full audit trail; deferred to a later iteration.
