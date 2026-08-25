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
* **Option 2:** PostgreSQL LISTEN/NOTIFY watcher (custom async implementation).
* **Option 3:** PostgreSQL LISTEN/NOTIFY watcher via `casbin-postgresql-watcher`.
* **Option 4:** Redis pub/sub watcher.

## Decision Outcome

Chosen option: *Option 2 — custom async PostgreSQL LISTEN/NOTIFY watcher*, because it uses the same mechanism as the official `casbin-postgresql-watcher` package but integrates natively with FastAPI's asyncio event loop, which is a better fit for this codebase.

The official `casbin-postgresql-watcher` package (`pip install casbin-postgresql-watcher`) implements the same PostgreSQL LISTEN/NOTIFY pattern and is the Casbin-recommended approach. It spawns a background process and communicates via a pipe to signal that a reload is needed. This works well for synchronous frameworks (Django, Flask) but requires bridging a sync subprocess into an asyncio lifespan, which adds more glue code than it saves. Since `asyncpg` is already a project dependency, implementing the same pattern natively in ~50 lines of async Python is simpler and avoids that bridging overhead. If `casbin-postgresql-watcher` adds async support in the future, switching to it is straightforward.

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

### Option 2 — Custom Async PostgreSQL LISTEN/NOTIFY Watcher

* Good, because it reuses the existing PostgreSQL instance — no new dependencies.
* Good, because policy changes propagate to all workers within milliseconds.
* Good, because the LRU cache continues to work between notifications.
* Good, because the asyncpg connection integrates natively with FastAPI's event loop.
* Neutral, because workers receive self-notifications (they both NOTIFY and LISTEN), triggering a redundant reload on the originating worker. The overhead is negligible.
* Bad, because there is a small window between startup and the first `load_policy()` where a worker's state may lag if role assignments happened while the service was down. This is mitigated by the existing `AUTHORIZER_STARTUP_SYNC` setting.

### Option 3 — `casbin-postgresql-watcher` Package

* Good, because it is the Casbin-recommended approach and uses the same LISTEN/NOTIFY mechanism.
* Good, because it reduces custom code to maintain.
* Bad, because the package is built for synchronous frameworks and internally uses `psycopg2` with a subprocess + pipe. Adapting this to FastAPI's async lifespan requires more bridging code than implementing the pattern directly.
* Neutral, because `asyncpg` is already a project dependency, so no new infrastructure is needed either way.

### Option 4 — Redis Pub/Sub Watcher

* Good, because Redis pub/sub is a well-established pattern supported natively by casbin watchers.
* Bad, because it requires adding Redis as a new infrastructure dependency.
* Neutral, because the casbin-redis-watcher library exists but brings additional operational overhead.
