---
description: Finds a real, reproducible bug and fixes it with a regression test
on:
  schedule: weekly on friday
  skip-if-match: 'is:open label:agent-bug'
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 60
sandbox:
  agent:
    runtime: docker-sudo-iptables
imports:
  - shared/background-agent.md
safe-outputs:
  report-failure-as-issue: false
  create-issue:
    title-prefix: "[bug] "
    labels: [background-agent, agent-bug, bug]
    expires: false
  create-pull-request:
    title-prefix: "[bug] "
    labels: [background-agent, agent-bug, bug]
  noop:
    report-as-issue: false
---

# Bug finder

Find the single most impactful real bug: code that does the wrong thing for a realistic input or state, and fix it.

Look across backend, plugins, frontend, SDK and CLI, for example: logic errors and wrong conditions, unhandled edge cases (empty, missing, duplicate, concurrent), state that is not updated or cleaned up, mismatches between the frontend and the API contract, broken lifecycle or status transitions, off-by-one and pagination errors, and errors that are swallowed silently.

Rank by user impact: data loss or corruption first, then wrong data shown or written, then broken flows. A suspicion is not a bug. Code you merely find unusual is not a bug.

## Evidence

Write a regression test that reproduces the bug. Run it on the unchanged code and confirm it fails, then apply the fix and confirm it passes. Include both test outputs in the issue and PR. If you cannot write a failing test, the bug is not proven: call `noop`.
