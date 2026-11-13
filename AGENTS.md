# AI Agent Guidelines for Data Product Portal

When creating code, keep it minimal and concise. Do not add comments or explain your code unless explicitly asked.

## Project Overview

The Data Product Portal manages data products and their output ports.
It consists of a 3-tier web architecture.

## Tech Stack and Directory Structure

*   `backend/`:See [backend/AGENTS.md](backend/AGENTS.md).
*   `frontend/`: See [frontend/AGENTS.md](frontend/AGENTS.md).
*   `cli/go`: Cli in Go
*   `plugins/`: The technical asset plugins the portal ships, published as `data-product-portal-plugins` and found through entry points. No plugin code lives in `backend/`.
*   `demo/`: Demo setups.
*   `docs/`: Docusaurus documentation and Architecture Decision Records (ADRs in `docs/adr/`). Do not edit versioned docs
*   `integrations/`: Platform-specific integration logic (Terraform, BitOL, data quality).
*   `helm/`: Kubernetes deployment charts.
*   `scripts/`: Build and utility scripts.

## Workflow & Automation

*   **Task Runner**: `Taskfile.yml` is primarily for release automation.
*   **Pre-commit**: Stage your change and run `scripts/precommit.sh` rather than invoking Ruff, mypy, or Biome directly. It sets up the backend environment (also in a worktree without its own venv), reruns the hooks until the generators (OpenAPI client, SDK, CLI, translations) stop changing files, and stages what they write. Commit only once it exits 0. Code must pass pre-commit hooks (Ruff, mypy, Biome, gitleaks, OpenAPI spec check).
*   **ADRs**: When adding major features or making architectural changes, consider if a new ADR (`docs/adr/`) is needed validate with user. Don't duplicate documentation — reference an existing doc instead of repeating its content.
*   **Agent Skills**: Issue tracker, triage labels and domain docs for skills are configured in `docs/agents/`.
*   **User DOCS**: When development is done, discuss ONCE with the user that the documentation (`docs/docs/`) including AGENTS.md files is complete and consistent.

## Development Process

Follow [Our Development Process](CONTRIBUTING.md#our-development-process). At the start of new work:

1. If the user gave an issue or link, read it with the tools you have; if you can't, ask them to paste it.
2. If there is no GitHub issue yet, offer to draft one (title, body, `bug` or `enhancement`, source link) and create it once the user says yes. If it isn't clear yet what they want, suggest a grilling session first.
3. Read the issue (see `docs/agents/issue-tracker.md`) and, if it has a linked PR (`closedByPullRequestsReferences`), the PR with `gh pr view <n> --json isDraft,reviews`. Propose the first matching next step:

| State | Next step |
|-------|-----------|
| UI change without a linked, signed-off design | Ask for the design link and its sign-off |
| `needs-triage` | Triage it (`/triage`): set a `ready-for-*`, `needs-info` or `wontfix` [label](CONTRIBUTING.md#labels) |
| `needs-info` or `wontfix` | Nothing to build; say so |
| Issue leaves open questions about what or how | Suggest a grilling session on the issue, or `/wayfinder` for big unclear work |
| Bug with unknown cause | `diagnosing-bugs` |
| Approach clear, no PR | Implement (`/implement`), for a bug with a regression test, and open a draft PR with `Closes #<n>` |
| Draft PR | `code-review` against `main` and the issue, then the Copilot loop, up to 3 rounds |
| Copilot has nothing useful left | Mark the PR ready, write the body with `pr-description` |

These are suggestions, not requirements: propose one step at a time, wait for the user's yes, and go along when they skip a step. A grilling session uses the `grilling` skill, which is what `/grill-me` runs. Skills written as `/name` only start when the user types them; suggest the command. At every step, flag when an ADR is needed and write it with the `adr` skill.

## General Rules for Agents

*   **Domain Language**: Use the terms defined in `CONTEXT.md` (e.g. Output Port, not Dataset; Access Type, not Classification) in code, docs and conversation.
*   **Analyze First**: Use search tools to find and replicate existing patterns before inventing new ones.
*   **Surgical Changes**: Modify only what is necessary. Avoid unsolicited refactoring. Edit files directly rather than through one-off scripts; split large edits into multiple steps if needed.
*   **Validation**: Always verify your changes.
*   **No Dead Code**: Before a commit, check for unused code, redundant returns, and dead statements — never leave them in.
*   **Failing Tests**: Fix and rerun failing tests one at a time; only rerun the full suite once everything passes.
*   **Writing style**: Don't over use bold or italic use in markdowns, only use it to be consistent
*   **One Concern per PR**: If you can't summarize the diff in one sentence, stop and propose splitting the work into separate branches/PRs before continuing. If the user persists in keeping the work don't mention this again.
