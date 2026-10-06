---
description: Finds the biggest code inconsistency in the backend and aligns it to the dominant pattern
on:
  schedule: weekly on wednesday
  skip-if-match: 'is:open label:agent-backend-consistency'
permissions:
  contents: read
  issues: read
  pull-requests: read
  copilot-requests: write
timeout-minutes: 60
sandbox:
  agent:
    runtime: docker-sudo-iptables
imports:
  - shared/background-agent.md
safe-outputs:
  create-issue:
    title-prefix: "[backend consistency] "
    labels: [background-agent, agent-backend-consistency]
    expires: false
  create-pull-request:
    title-prefix: "[backend consistency] "
    labels: [background-agent, agent-backend-consistency]
  noop:
    report-as-issue: false
---

# Backend code consistency

Find the biggest inconsistency in how the backend (including the plugins) does the same thing in different ways, and align it to one pattern.

Examples of what to compare: how routers, services and schemas are layered and split, how authorization is checked, how errors are raised and mapped to HTTP responses, how database sessions and transactions are handled, how queries are written, how events and notifications are emitted, naming of endpoints, functions, schemas and tests, and use of the domain terms from `CONTEXT.md`.

The target pattern is the one `backend/AGENTS.md` prescribes; if it says nothing, the one most of the codebase already uses. Never introduce a new pattern. Do not change public API paths, request or response shapes, or database schemas. Rank by how many places diverge and how much the divergence costs readers and maintainers. Keep the change reviewable: if the inconsistency is spread too wide for one PR, fix one coherent slice and list the remaining places in the issue.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. The full backend test suite and pre-commit must pass, which shows behaviour is unchanged.
