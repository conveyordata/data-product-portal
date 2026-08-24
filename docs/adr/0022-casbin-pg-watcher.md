# Casbin Policy Synchronization via PostgreSQL LISTEN/NOTIFY

## Context and Problem Statement

The Data Product Portal uses Casbin as its RBAC authorization engine. Casbin's adapter reads policies from PostgreSQL into an in-memory enforcer at startup. When a role assignment is created or revoked in one process, only that process updates its in-memory state. Other processes — including those handling persistent MCP connections — never learn about the change and continue enforcing stale policies.

This manifests as authorization failures for non-admin users of the MCP tools (`query_athena`, `list_glue_tables`, etc.) who have valid role assignments but whose requests happen to hit a worker that still holds a stale enforcer snapshot.

## Decision Drivers

* No new infrastructure dependencies — the system already runs PostgreSQL.
* Minimal latency between role assignment and policy taking effect across all workers.
* The fix must work with Gunicorn / uvicorn multi-worker deployments and with sticky MCP connections.
* Avoid per-request database round-trips for authorization checks (preserve the LRU cache).

## Considered Options

* **Option 1:** Reload casbin policy on every authorization check.
* **Option 2:** PostgreSQL LISTEN/NOTIFY watcher.
* **Option 3:** Redis pub/sub watcher.

## Decision Outcome

Chosen option: *Option 2 — PostgreSQL LISTEN/NOTIFY watcher*, because it propagates policy changes to all workers in near-real-time without adding external dependencies or per-request overhead.

Each worker starts a long-lived asyncpg connection that LISTENs on the `casbin_policy_update` channel. When `Authorization._after_update()` is called — after any `assign`, `revoke`, or `sync` operation — it sends `NOTIFY casbin_policy_update` via the shared SQLAlchemy engine. All listening workers receive the notification and call `enforcer.load_policy()` followed by a cache clear, bringing their in-memory state back in sync with the database.

### Confirmation

* Assigning a data product role in one worker propagates to all workers within milliseconds.
* If the watcher connection drops (e.g. during a PostgreSQL failover), the background task reconnects automatically with a 5-second back-off.
* `Authorization.reload_policy()` is exposed so the watcher can call it without coupling the watcher module to the `Authorization` class.
* Existing unit tests remain unaffected because `notify_policy_update()` swallows connection errors.

## Pros and Cons of the Options

### Option 1 — Reload on Every Authorization Check

* Good, because every check is guaranteed to see the latest state.
* Bad, because it removes all benefit of the LRU cache.
* Bad, because it adds a synchronous database query to every authorization decision, increasing latency and database load.

### Option 2 — PostgreSQL LISTEN/NOTIFY Watcher

* Good, because it reuses the existing PostgreSQL instance — no new dependencies.
* Good, because policy changes propagate to all workers within milliseconds.
* Good, because the LRU cache continues to work between notifications.
* Good, because the asyncpg connection is cheap and the implementation is small.
* Neutral, because workers receive self-notifications (they both NOTIFY and LISTEN), triggering a redundant reload on the originating worker. The overhead is negligible.
* Bad, because there is a small window between startup and the first `load_policy()` where a worker's state may lag if role assignments happened while the service was down. This is mitigated by the existing `AUTHORIZER_STARTUP_SYNC` setting.

### Option 3 — Redis Pub/Sub Watcher

* Good, because Redis pub/sub is a well-established pattern supported natively by casbin watchers.
* Bad, because it requires adding Redis as a new infrastructure dependency.
* Neutral, because the casbin-redis-watcher library exists but brings additional operational overhead.
