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

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. The full backend test suite and pre-commit must pass, which shows behaviour is unchanged.
