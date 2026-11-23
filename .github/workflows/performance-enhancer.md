---
name: "Background agent: Performance"
description: Finds the most significant performance problem and fixes it without changing behaviour
on:
  schedule: weekly on monday
  skip-if-match: 'is:open label:agent-performance'
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
    title-prefix: "[performance] "
    labels: [background-agent, agent-performance]
    expires: false
  create-pull-request:
    draft: false
    title-prefix: "[performance] "
    labels: [background-agent, agent-performance]
    github-token-for-extra-empty-commit: none
  noop:
    report-as-issue: false
---

# Performance enhancer

Find the single most inefficient piece of code whose fix gives a significant, measurable gain, and fix it without losing functionality or adding complexity.

## Required survey

Look across backend, frontend, SDK and CLI, and do every check:

1. N+1 queries and missing eager loading.
2. Queries that load far more rows or columns than are used.
3. Missing database indexes on filtered or joined columns.
4. Repeated work inside loops.
5. Quadratic algorithms over growing collections.
6. Unnecessary React re-renders and over-fetching from the API.
7. Large synchronous work on hot request paths.

Only consider code on a path that actually runs often or on growing data. Micro-optimisations do not qualify.

## Evidence

Measure before and after on the same setup: query counts, timings, or a benchmark script (never add benchmarked scripts to the repo), with the numbers in the issue and PR. Where practical, add a regression test that locks in the gain (for example asserting the query count). Existing tests must keep passing to show behaviour is unchanged.
