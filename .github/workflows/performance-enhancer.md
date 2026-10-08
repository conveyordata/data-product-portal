---
description: Finds the most significant performance problem and fixes it without changing behaviour
on:
  schedule: weekly on monday
  skip-if-match: 'is:open label:agent-performance'
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
    title-prefix: "[performance] "
    labels: [background-agent, agent-performance]
    expires: false
  create-pull-request:
    title-prefix: "[performance] "
    labels: [background-agent, agent-performance]
  noop:
    report-as-issue: false
---

# Performance enhancer

Find the single most inefficient piece of code whose fix gives a significant, measurable gain, and fix it without losing functionality or adding complexity.

Look across backend, frontend, SDK and CLI, for example: N+1 queries or missing eager loading, queries that load far more rows or columns than used, missing database indexes on filtered or joined columns, repeated work inside loops, quadratic algorithms over growing collections, unnecessary React re-renders or over-fetching from the API, and large synchronous work on hot request paths.

Only consider code on a path that actually runs often or on growing data. Micro-optimisations do not qualify.

## Evidence

Measure before and after on the same setup: query counts, timings, or a benchmark script (never add benchmarked scripts to the repo), with the numbers in the issue and PR. Where practical, add a regression test that locks in the gain (for example asserting the query count). Existing tests must keep passing to show behaviour is unchanged.
