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

The target pattern is the one the documents below prescribe, else the one most of the codebase already uses. Never introduce a new pattern. Do not change public API paths, request or response shapes, or database schemas.

## What to hold the code to

The rules in `AGENTS.md` and `backend/AGENTS.md`, and the terms in `CONTEXT.md`, over `backend/app/` and `plugins/`. Go through them section by section, and compare modules that do the same job. Rename internal names only; never API paths, schema field names or database columns. Fix one test module per PR.

## Kinds of defect to look for

Examples, not a complete list:

1. Business logic, queries, authorization decisions or HTTP errors in the wrong layer.
2. Modules split into files differently from the rest.
3. Relationship loading the written rules don't allow.
4. The same kind of value stored or compared in two forms.
5. Visibility, admin and authorization decisions made outside the place that owns them, and routes without an authorization check.
6. Internal names that use a term `CONTEXT.md` lists under _Avoid_.
7. Tests named or built differently from the written rules.
8. The same check, query or mapping written out in several places instead of shared.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. The full backend test suite and pre-commit must pass, which shows behaviour is unchanged.
