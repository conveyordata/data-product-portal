# Backend Agent Guidelines

Extends the root [AGENTS.md](../AGENTS.md) — read that first.

## Tooling
* FastAPI, SQLAlchemy, Alembic (Postgres), Casbin (RBAC), pgvector (embeddings), Pydantic v2, FastMCP. Tooling used includes Poetry, Ruff, mypy, pytest.

## Architecture

*   Adhere strictly to the separation of `router.py`, `service.py`, `model.py`, `schema_request.py`, and `schema_response.py`. Business logic belongs in `service.py`. `router.py` only wires requests/responses. `model.py` only defines persistence, don't add business logic there.
*   Never import from the generated SDK/client package in backend code.

## Schemas & Data

*   Strictly use Pydantic v2 for validation. Differentiate between request (`schema_request.py`) and response (`schema_response.py`) schemas.


## Authorization
*   When creating new endpoints check with the user if authorization is needed with `Authorization.enforce()`.
In principle should always be present on non GET endpoints and sensitive GET endpoints.
* Check if new actions need to be added.

## SQLAlchemy
*   SQLAlchemy: use `joined` lazy loading for 1:1 relationships; otherwise use `raise` and specify explicit eager loading.
*   No enums in the database — store strings, use `Enum`s in Pydantic models, and reuse existing enums where possible.
*   Use SQLAlchemy async models and Alembic for migrations (`backend/app/database/alembic/versions/`).

## Testing

*   Run `task test:backend` (or `poetry run pytest -v tests/`). Tests live in `backend/tests/`, organized to mirror `backend/app/`.
*   Name tests `test_<method_name>__<scenario>`.
*   Use factories to build test data.
*   Every new route must ship with full test coverage.

## Running Commands

*   Use `poetry run` to execute backend scripts/commands.
