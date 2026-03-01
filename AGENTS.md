# AI Agent Guidelines for Data Product Portal

Welcome! These guidelines will help you navigate and contribute effectively to the Data Product Portal codebase. Keep this context concise to minimize token usage while retaining critical architectural boundaries.

## Project Overview
The Data Product Portal manages data products and their output ports. It consists of a multi-tier architecture with a FastAPI backend, a React frontend, a CLI, and comprehensive documentation.

## Tech Stack
*   **Backend**: Python, FastAPI, SQLAlchemy, Alembic, Casbin (RBAC).
*   **Frontend**: React, TypeScript, Vite, Biome (linting/formatting), i18next (localization).
*   **CLI**: Go, Python.
*   **Docs**: Docusaurus.
*   **Tooling**: `Taskfile.yml` (automation), Docker, Helm.

## Directory Structure
*   `backend/app/`: Python API. Follows Service-Router-Model-Schema pattern.
*   `frontend/`: React SPA.
*   `cli/`: Command-line tools (Go & Python).
*   `demo/`: Demo setups.
*   `docs/`: Docusaurus documentation and Architecture Decision Records (ADRs).
*   `integrations/`: Platform-specific integration logic.
*   `helm/`: Kubernetes deployment charts.

## Backend Guidelines
*   **Architecture**: Features are modularly isolated in `backend/app/<feature>/` (e.g., `data_products`). Adhere strictly to the separation of `router.py`, `service.py`, `model.py`, `schema_request.py`, and `schema_response.py`.
*   **Schemas**: Strictly use Pydantic for validation. Differentiate between request (`schema_request.py`) and response (`schema_response.py`) schemas.
*   **Authorization**: The system uses Casbin for fine-grained RBAC. Always apply `Authorization.enforce()` dependencies on new routers and endpoints.
*   **Database**: Use SQLAlchemy models and Alembic for migrations.

## Frontend Guidelines
*   **Types**: Ensure TypeScript interfaces strictly match the backend's OpenAPI schemas.
*   **Localization**: Use `i18next` for all user-facing strings. No hardcoded text.
*   **Code Quality**: The project uses Biome for linting and formatting. Ensure generated code adheres to these standards.

## Workflow & Automation
*   **Task Runner**: Use `task` (via `Taskfile.yml`) as the primary entry point for development scripts.
*   **OpenAPI Updates**: If you modify backend routes or schemas, run `task update:open-api-spec` to regenerate the OpenAPI specification before completing the task.
*   **Pre-commit**: Code must pass `pre-commit` hooks.
*   **Documentation**: When adding major features or making architectural changes, consider if a new ADR (`docs/adr/`) is needed.

## General Rules for Agents
*   **Analyze First**: Use search tools to find and replicate existing patterns before inventing new ones.
*   **Surgical Changes**: Modify only what is necessary. Avoid unsolicited refactoring.
*   **Validation**: Always verify your changes (e.g., running `pytest` for the backend).
