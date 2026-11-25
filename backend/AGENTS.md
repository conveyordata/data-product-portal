# Backend Agent Guidelines

Extends the root [AGENTS.md](../AGENTS.md) — read that first.

## Tooling
* FastAPI, SQLAlchemy, Alembic (Postgres), Casbin (RBAC), pgvector (embeddings), Pydantic v2, FastMCP. Tooling used includes Poetry, Ruff, mypy, pytest.

## Architecture

*   Adhere strictly to the separation of `router.py`, `service.py`, `model.py`, `schema_request.py`, and `schema_response.py`. Business logic belongs in `service.py`. `router.py` only wires requests/responses. `model.py` only defines persistence, don't add business logic there.
*   Never import from the generated SDK/client package in backend code.
*   Place private helper methods below the public methods that use them, so readers see the high-level flow before its implementation details.

## Schemas & Data

*   Strictly use Pydantic v2 for validation. Differentiate between request (`schema_request.py`) and response (`schema_response.py`) schemas.


## Authorization
*   When creating new endpoints check with the user if authorization is needed with `Authorization.enforce()`.
In principle should always be present on non GET endpoints and sensitive GET endpoints.
* Check if new actions need to be added.
* Content tied to a resource (notifications, counts, graph nodes) follows that resource's visibility.
* A visibility filter can turn a related object into `None`; guard every consumer of that relationship. Visibility filters are for reads: writes, approvals, deletes and in-use checks run with `UNFILTERED` (it skips both the Data Product visibility and the Output Port access filter), tested with the counterpart row hidden.
* When you widen an authorization or visibility rule, list every read path it opens and add a negative test for each.
* When acting on "the active" grant, request or assignment, check whether several can be active at once and handle all of them.
* When a write changes role assignments or group membership, update the Casbin enforcer in that write, not only on reload. Mirror new `AuthorizationAction`s in `frontend/src/types/authorization/rbac-actions.ts`.
* Who sees a Data Product, Exploration, Technical Asset or Output Port is decided in `app/database/visibility.py`, and who is an admin in `app/authorization/role_assignments/global_/admin.py`; don't read `session.info` or write visibility or admin predicates elsewhere.

## SQLAlchemy
*   SQLAlchemy: use `joined` lazy loading for 1:1 relationships; otherwise use `raise` and specify explicit eager loading.
*   No enums in the database — store strings, use `Enum`s in Pydantic models, and reuse existing enums where possible.
*   Use SQLAlchemy async models and Alembic for migrations (`backend/app/database/alembic/versions/`).
*   The backend can run as several replicas: enforce uniqueness and invariants with a database constraint or `SELECT ... FOR UPDATE`, never with only a prior `SELECT` or an in-process lock.
*   Update `EventTrackedMixin` models through ORM attributes, not bulk `update()`, so events fire.
*   After a rebase, core and each plugin migration directory must each still have exactly one head (`migrate_all` fails otherwise); several heads overall are expected. A downgrade must handle rows the upgrade allowed, and a backfill must pass the same validation as new writes.

## Testing

*   Run `task test:backend` (or `poetry run pytest -v -n logical --dist worksteal tests/` in the `backend` folder, after starting Postgres with `task db:up`). Leave out `-n` for a single test or file; see `test:backend` in [Taskfile.yml](../Taskfile.yml) for why. Tests live in `backend/tests/`, organized to mirror `backend/app/`.
*   Name tests `test_<method_name>__<scenario>`.
*   Use factories to build test data.
*   Each test runs in a transaction that is rolled back afterwards. Assert row locks with `row_lock_modes` from `tests/session_util.py` instead of a second connection. Mark a test `@pytest.mark.commits` only when its data must be visible to another connection, like migrations; its tables are truncated afterwards.
*   Every new route must ship with full test coverage.
*   If you want to test a data migration, do it in `tests/app/database/alembic/versions/test_<revision>_<slug>.py`, using `before_migration`. That way the next data migration follows the same pattern.

## Running Commands

*   Use `poetry run` to execute backend scripts/commands.
