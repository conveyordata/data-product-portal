# Split Input Ports into a Link and Access Requests

## Context and Problem Statement

Time-bound access to output ports is currently modelled on a single `input_ports` table. That table conflates two very different concepts: the **relationship** (a consumer consumes an output port) and the **access request/grant lifecycle** (who requested, who decided, when it expires). As a result it is hard to keep an auditing log of renewals and denials, and the state of the read access is mixed with the state of the request.

The current implementation uses an `EXPIRED` status flipped by an hourly background task, an `is_renewing` boolean, `total_range_start/end` bookkeeping, and renewal logic that *mutates the existing grant row in place*, losing history. Edge cases such as "access is still valid, a renewal was requested and then denied" cannot be represented cleanly. The upcoming feature to allow a justification on a denied access request is also not possible in the current model.

**Core question: how should the access relationship, its request/decision history, and the current grant be modelled?**

## Decision Drivers

* Auditability — keep a history of requests, renewals and denials instead of overwriting one row
* Renewals without losing history — a renewal must not mutate the previous grant
* Support a denial justification (upcoming feature)
* Separate the *relationship* from the *request/decision* from the *grant* (a time-bounded window)
* Remove the hourly background task by computing access and expiry live as this introduces extra risk and complexity
* Minimise refactoring and stay backward-compatible for already-released clients (frontend, published SDK, Go CLI)

## Considered Options

* **Option 1: Keep the single `input_ports` table** — extend it with more flags and dates to cover renewals, denials and expiry.
* **Option 2: Split into `input_ports` (link) + `input_port_requests`** — a lightweight link plus one row per access request/grant, with access and expiry computed from the requests.

This mirrors how identity-governance systems (e.g. Entra PIM, Google Cloud IAM) model access: separate the relationship, the request/decision (an append-only audit trail), and the grant (a time-bounded window evaluated live).

## Decision Outcome

**Chosen option: Option 2 — split into `input_ports` and `input_port_requests`.**

The link table keeps only identity (which consumer consumes which output port). Every request or renewal is a new row in `input_port_requests`, so history is preserved and denials/renewals are auditable. Whether a link currently grants access is computed live from its approved, non-expired requests; expiry (`is_expired`, `is_expiring_soon`) is computed from `valid_until`. This removes the need for the background task.

### Confirmation

* A new `input_port_requests` table exists; `input_ports` is reduced to identity columns.
* Requesting access, renewing, approving, denying and revoking operate on request rows, not on the link.
* The `expire_input_ports` background task, the `is_renewing` flag and the `EXPIRED` status are removed.
* A migration backfills one request per existing link and drops the moved columns.
* Backward compatibility is preserved for released clients (see Backward compatibility below).

## Pros and Cons of the Options

### Option 1: Keep the single table

* **Good, because** no schema split and no migration of existing rows.
* **Neutral, because** it keeps the model familiar to the current code.
* **Bad, because** renewals overwrite the grant in place, so there is no history.
* **Bad, because** denials and renewals cannot be audited, and a denial justification cannot be added.
* **Bad, because** it needs an `EXPIRED` status maintained by a background task and an `is_renewing` flag to track in-flight renewals.

### Option 2: Split into link + requests

* **Good, because** every request/renewal/denial is its own row — full history and audit trail.
* **Good, because** an active grant can coexist with a pending or denied renewal.
* **Good, because** access and expiry are computed live, removing the background task and its edge cases.
* **Good, because** a denial justification fits naturally on the request row.
* **Neutral, because** the "does this link currently grant access" signal must be re-expressed (see Open Questions).
* **Bad, because** it requires a new table and a one-time backfill migration.

## Design Details

### `input_ports` — the link (output port ↔ consumer)

Keep (identity only):

| Column | Meaning |
| --- | --- |
| `id` | PK |
| `dataset_id` → datasets | the output port |
| `consuming_abstract_data_product_id` → abstract_data_products | the consuming data product / exploration |
| `created_on`, `updated_on` | audit |

Add:

| Add | Meaning |
| --- | --- |
| link access indicator — reused `status`, or a new `is_active` | how the link signals "has access" for counts / graph / ordering / filtering; derived from its requests, not stored. Two options — see Open Questions. |

Remove (moved to `input_port_requests`, or dropped as now computed):

| Removed column | What happens to it |
| --- | --- |
| `justification` | moved to the request (each request has its own reason; also allows a denial justification later) |
| `status` | moved to the request (see Open Questions for what the link keeps) |
| `requested_on`, `requested_by_id` | moved to the request |
| `approved_on`, `approved_by_id` | moved to the request as `decided_on` / `decided_by_id` |
| `denied_on`, `denied_by_id` | moved to the request as `decided_on` / `decided_by_id` |
| `renewed_on`, `renewed_by_id` | dropped — a renewal is its own request; its `decided_on` / `decided_by` is the "renewed by/on" |
| `is_renewing` | dropped — a renewal in flight is a PENDING request on the link |
| `expired_on` | dropped — expiry is computed from `valid_until` |
| `expires_on` | moved to the request as `valid_until` |
| `total_range_start` | moved to the request as `valid_from` |
| `total_range_end` | dropped — same value as `valid_until`; the overall span is derived from the request history |
| `requested_duration_days` | moved to the request |

### `input_port_requests` — the new table (one row per request)

Requests reference the link one-directionally via `input_port_id`; the link holds no request list.

| Column | Meaning |
| --- | --- |
| `id` | PK |
| `input_port_id` → input_ports | the link this request belongs to |
| `status` | PENDING → APPROVED / DENIED |
| `justification` | the consumer's reason for this request; on a renewal the previous request's justification is reused |
| `requested_duration_days` (nullable) | requested window length; NULL = permanent |
| `requested_on`, `requested_by_id` → users | when / who requested |
| `decided_on` (nullable), `decided_by_id` (nullable) → users | when / who approved or denied (which one is told by `status`) |
| `valid_from` (nullable) | start of the granted window (set at approval) |
| `valid_until` (nullable) | end of the granted window; NULL = permanent |
| `created_on`, `updated_on` | audit |

Constraint: at most one PENDING request per link (partial unique index). A new request is allowed at any time as long as none is currently pending.

### Access and expiry are computed

Nothing here is stored or maintained by a job — everything is evaluated live from the requests.

* `is_expired` (request) — true when an APPROVED request's `valid_until` is in the past.
* `is_expiring_soon` (request) — true when an APPROVED request is within the expiring-soon threshold of `valid_until`. Computed in the backend and returned by the API; drives the renew button and warning banner.
* `status` (request) — the stored decision: PENDING → APPROVED / DENIED.

The frontend composes its display badge from these plus the access indicator; there is no separate stored status field for the display.

### Endpoint changes

All paths stay on `/api/v2`; changes are additive.

**Consumer side** (a data product or exploration managing what it consumes):

* `GET /data_products/{id}/input_ports` and `GET /explorations/{id}/input_ports` — list a consumer's input ports. Response adds `is_expired`, `is_expiring_soon`, the effective end date (`valid_until`) and the request history; grant fields come from the active request, not the flat link.
* `POST /data_products/{id}/input_ports` and `POST /explorations/{id}/input_ports` — request access; also the single entry point for renewal. If a link already exists for that (consumer, output port), it adds a new request instead of failing as "already exists" or mutating the old grant; on a renewal the previous justification is reused. Blocked only if a request is already PENDING on that link.
* `DELETE /data_products/{id}/input_ports/{output_port_id}` (and exploration equivalent) — unlink;

**Producer side** (an output port owner managing consumers):

* `GET /data_products/{dp}/output_ports/{op}/input_ports` — list the consumers of an output port; same additive response changes as the consumer list.
* `POST .../input_ports/approve` and `POST .../input_ports/deny` — decide the link's single PENDING request; sets `status` and `decided_by/on`, and on approve sets `valid_from/valid_until` from the requested duration.
* `POST .../input_ports/renew` — producer-initiated extension; adds a new APPROVED request (`decided_by` = the producer) rather than overwriting the current grant's dates.
* `POST .../input_ports/remove` — revoke; deletes the link

**Approver queue:**

* `GET /users/current/pending_actions` — includes pending input-port requests. The item sources its who/when/duration fields from the request and adds `decided_by`; `approved_by` / `denied_by` are kept as deprecated aliases (from `decided_by`) for one release.

### Edge cases and outcomes

| # | Scenario | Outcome                                                                                              |
| --- | --- |------------------------------------------------------------------------------------------------------|
| 1 | Unrestricted OP, permanent | Request auto-approved, `valid_until=NULL` → has access, no expiry                                    |
| 2 | Unrestricted OP, time-bound | Auto-approved, `valid_from=now`, `valid_until=now+days` → access until it lapses                     |
| 3 | Restricted OP, time-bound, request | Request PENDING (`requested_duration_days` set) → no access; on approve → `valid_from/until` set     |
| 4 | Restricted OP request denied | Request DENIED; the link stays, shown as denied; no access                                           |
| 5 | Re-request after denial | New request on the same link — no duplicate link                                                     |
| 6 | Active grant + renewal denied | R1 still active → has access; R2 shown as denied. Both visible in history                            |
| 7 | Active grant + renewal approved | R2 approved with a later `valid_until`; effective end = latest window; R1 historical                 |
| 8 | Renewal after expiry | Old grant lapsed → no access; renewal request → approve → has access again                           |
| 9 | Expiring soon | Backend sets `is_expiring_soon` from `valid_until`; UI shows renew button + warning; no state change |
| 10 | Permanent grant | `valid_until=NULL` → no expiry, no extend                                                            |
| 11 | Producer extend | Producer adds a new approved request (`decided_by` = producer)                                       |
| 12 | Second request while one pending | Blocked (one pending per link) → 400; DB partial-unique-index backstop                               |
| 13 | Remove / unlink | Delete the link -> Maybe w never want to delete the ink, just put it on inactive to keep the audit   |
| 14 | Grant lapses while renewal still pending | No access until re-approval (a natural gap — replaces today's "renewing → PENDING")                  |

## Open Questions

### Link access indicator — reuse `status` vs a new `is_active`

The link needs a queryable "does this consumer currently have access" signal for internal SQL — the approved-input-port counts, the lineage-graph edge, ordering and filtering. Today this is `input_ports.status`. Two ways to carry it forward; this needs a team decision.

* **Option A — reuse `status` on the link.** Keep a `status` field on the link, derived from the latest request (`approved / pending / denied`).
  * **Good, because** the existing `input_ports.status` order-by, count subqueries, graph query and checks keep working with little to no refactoring.
  * **Bad, because** `status = approved` no longer means "has access right now" — an approved-but-expired request is still `approved`, so a check that needs live access must also look at `valid_until`.
  * **Bad, because** the link's `status` mirrors the latest request, so a link with an active grant and a newer pending renewal reads `pending`; "still has access while a renewal is in flight" is only visible via `valid_until`.

* **Option B — a new `is_active` boolean.** Computed "currently grants access" (approved and window open).
  * **Good, because** it is unambiguous, including while a renewal is pending.
  * **Bad, because** the `status`-based counts, graph query and order-by must be refactored to use it.

### Should this ADR include a decision backgorund-task vs computed fields as well?

One of the main outcomes is that we remove a background task and introduce more computed fields in the backend.
Is this also part of this ADR as a general decision, or is thsi function creep?

### Do we allow deletes on input ports?

Deleting an input port and wihtout a cascade keeps the history of the audit, but not the link to the port. Do we want to keep the input_port itself?
