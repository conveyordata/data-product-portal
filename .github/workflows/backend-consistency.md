---
name: "Background agent: Backend consistency"
description: Finds the biggest code inconsistency in the backend and aligns it to the dominant pattern
on:
  schedule: weekly on wednesday
  skip-if-match: 'is:open label:agent-backend-consistency'
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 60
runs-on: ubuntu-24.04
sandbox:
  agent:
    runtime: docker-sudo-iptables
imports:
  - shared/background-agent.md
safe-outputs:
  report-failure-as-issue: false
  create-issue:
    title-prefix: "[backend consistency] "
    labels: [background-agent, agent-backend-consistency]
    expires: false
  create-pull-request:
    draft: false
    title-prefix: "[backend consistency] "
    labels: [background-agent, agent-backend-consistency]
    github-token-for-extra-empty-commit: none
  noop:
    report-as-issue: false
---

# Backend code consistency

Find the biggest inconsistency in how the backend (including the plugins) does the same thing in different ways, and align it to one pattern.

The target pattern is the one `backend/AGENTS.md` prescribes, else the canonical module named below, else the one most of the codebase already uses. Never introduce a new pattern. Do not change public API paths, request or response shapes, or database schemas.

## Required survey

Read `backend/AGENTS.md`. Use `backend/app/data_products/output_ports/` (`router.py`, `service.py`, `model.py`, `schema_request.py`, `schema_response.py`) as the canonical module layout. Run every check over `backend/app/` and `plugins/`.

1. Layering. Business logic, queries, authorization decisions and `raise HTTPException` in a `router.py` instead of its `service.py` (`backend/AGENTS.md:10`). Count per router. For example `configuration/platforms/router.py`, `resource_names/router.py`, `configuration/access_durations/router.py` and `data_products/output_ports/contract/router.py` raise in the router, while services raise in more than 100 places.
2. File split. Modules without separate `schema_request.py` and `schema_response.py`, request and response schemas mixed in one file, and logic in `model.py` (`backend/AGENTS.md:10,16`).
3. Relationship loading. Count each `lazy=` value in every `model.py`. `backend/AGENTS.md:26` allows `joined` for 1:1 and `raise` otherwise. List every `selectin` and `select`.
4. Enum columns. Columns declared with `values_callable` (store the value) against ones without it (store the name), and code or `backend/sample_data.sql` that compares or writes the other form (`.name` against `.value`). Count both variants.
5. Visibility and admin. Visibility or admin predicates, or reads of `session.info`, outside `app/database/visibility.py` and `app/authorization/role_assignments/global_/admin.py` (`backend/AGENTS.md:23`).
6. Authorization. Every `post`, `put`, `patch` and `delete` route, and every sensitive `get`, has an `Authorization.enforce(...)` dependency as in `data_products/output_ports/router.py` (`backend/AGENTS.md:20-21`). List the routes that don't.
7. Domain terms. Internal identifiers (classes, functions, variables, test names) that use a term `CONTEXT.md` lists under _Avoid_, for example `Dataset*` for Output Port or `data_output` for Technical Asset. Rename internal names only; never API paths, schema field names or database columns.
8. Tests. Test functions not named `test_<method_name>__<scenario>`, and test data built by hand where a factory in `backend/tests/factories/` exists (`backend/AGENTS.md:33-34`). Fix one test module per PR.
9. Helper placement. Private helpers placed above the public methods that use them (`backend/AGENTS.md:12`).
10. Repeated logic. The same check, query or mapping written out in two or more services or routers instead of shared, for example the role-assignment decide endpoints that #4714 aligned.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. The full backend test suite and pre-commit must pass, which shows behaviour is unchanged.
