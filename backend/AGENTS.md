# Backend Agent Guidelines

Extends the root [AGENTS.md](../AGENTS.md) — read that first.

## Architecture

*   Features are modularly isolated in `backend/app/<feature>/` (e.g., `data_products`). Adhere strictly to the separation of `router.py`, `service.py`, `model.py`, `schema_request.py`, and `schema_response.py`.
*   Business logic belongs in `service.py`. `router.py` only wires requests/responses. `model.py` only defines persistence, don't add business logic there.
*   Never import from the generated SDK/client package in backend code.

## Schemas & Data

*   Strictly use Pydantic v2 for validation. Differentiate between request (`schema_request.py`) and response (`schema_response.py`) schemas.
*   No enums in the database — store strings, use `Enum`s in Pydantic models, and reuse existing enums where possible.
*   SQLAlchemy: use `joined` lazy loading for 1:1 relationships; otherwise use `raise` and specify explicit eager loading.

## Authorization & Database

*   The system uses Casbin for fine-grained RBAC. Always apply `Authorization.enforce()` dependencies on new routers and endpoints.
*   Use SQLAlchemy async models and Alembic for migrations (`backend/app/database/alembic/versions/`).

## Testing

*   Run `task test:backend` (or `poetry run pytest -v tests/`). Tests live in `backend/tests/`, organized to mirror `backend/app/`.
*   Name tests `test_<method_name>__<scenario>`.
*   Use factories to build test data.
*   Every new route must ship with full test coverage.

## Events

*   When adding a new event, add it in both the backend and `frontend/src/types/events/event-types.ts`.

## Running Commands

*   Use `poetry run` to execute backend scripts/commands.
