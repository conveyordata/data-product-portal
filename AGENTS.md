# AI Agent Guidelines for Data Product Portal

When creating code, keep it minimal and concise. Do not add comments or explain your code unless explicitly asked.

## Project Overview

The Data Product Portal manages data products and their output ports.
It consists of a 3-tier web architecture.

## Tech Stack and Directory Structure

*   `backend/`: Backend written with FastAPI, SQLAlchemy, Alembic, Casbin (RBAC), pgvector (embeddings), Pydantic v2, FastMCP. Tooling used includes Poetry, Ruff, mypy, pytest. See [backend/AGENTS.md](backend/AGENTS.md).
*   `frontend/`: React 19, TypeScript, Vite, Redux Toolkit + RTK Query, Ant Design, Biome (linting/formatting), i18next (localization), Vitest (testing). See [frontend/AGENTS.md](frontend/AGENTS.md).
*   `cli/go`: Cli in Go
*   `demo/`: Demo setups.
*   `docs/`: Docusaurus documentation and Architecture Decision Records (ADRs in `docs/adr/`).
*   `integrations/`: Platform-specific integration logic (Terraform, BitOL, data quality).
*   `helm/`: Kubernetes deployment charts.
*   `scripts/`: Build and utility scripts.

## Workflow & Automation

*   **Task Runner**: `Taskfile.yml` is primarily for release automation.
*   **Pre-commit**: Run `pre-commit` rather than invoking Ruff, mypy, or Biome directly — it also regenerates the OpenAPI client/SDK. Code must pass pre-commit hooks (Ruff, mypy, Biome, gitleaks, OpenAPI spec check).
*   **Documentation**: When adding major features or making architectural changes, consider if a new ADR (`docs/adr/`) is needed. Don't duplicate documentation — reference an existing doc instead of repeating its content.
*   **Documentation**: When developing is done with the user ONCE that the documentation is complete and consistent.

## General Rules for Agents

*   **Analyze First**: Use search tools to find and replicate existing patterns before inventing new ones.
*   **Surgical Changes**: Modify only what is necessary. Avoid unsolicited refactoring. Edit files directly rather than through one-off scripts; split large edits into multiple steps if needed.
*   **Validation**: Always verify your changes.
*   **No Dead Code**: Before a commit, check for unused code, redundant returns, and dead statements — never leave them in.
*   **Failing Tests**: Fix and rerun failing tests one at a time; only rerun the full suite once everything passes.
*   **File Formatting**: Always leave a trailing empty line at the end of a file.
*   **Writing style**: Don't over use bold or italic use in markdowns, only use it to be consistent
*   **Boyscout Rule**: When touching code and you see legacy concepts, inefficient code, dead code or bugs, fix it. Only if the refactor is small enough,
otherwise suggest making a separate issue from it in github with the changes that an agent can pick up later.
*   **One Concern per PR**: If you can't summarize the diff in one sentence, stop and propose splitting the work into separate branches/PRs before continuing. If the user persists in keeping the work don't mention this again.
