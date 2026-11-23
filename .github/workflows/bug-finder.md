---
name: "Background agent: Bug finder"
description: Finds a real, reproducible bug and fixes it with a regression test
on:
  schedule: weekly on friday
  skip-if-match: 'is:open label:agent-bug'
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
    title-prefix: "[bug] "
    labels: [background-agent, agent-bug, bug]
    expires: false
  create-pull-request:
    draft: false
    title-prefix: "[bug] "
    labels: [background-agent, agent-bug, bug]
    github-token-for-extra-empty-commit: none
  noop:
    report-as-issue: false
---

# Bug finder

Find the single most impactful real bug: code that does the wrong thing for a realistic input or state, and fix it.

## Kinds of defect to look for

For each pattern, look for a concrete case and try to write a test that fails on the current code. The first case whose test fails is the bug you fix.

1. Two representations. The same value stored or compared in two forms: an enum by name against by value, local time against UTC, an id against a name.
2. Read filters on writes. Writes that go through a read filter (visibility, soft delete, scope) and so skip or break on rows the caller can't see.
3. Stale derived state. Data copied from a source of truth that isn't updated when the source changes, expires or is deleted.
4. Overlaps and edges. Ranges, durations and versions that overlap or meet at an edge: the first or last day, or two active records where the code expects one.
5. State transitions. Actions allowed or blocked in the wrong state, and guards that count the wrong states.
6. Unvalidated input. Input the API accepts that later breaks a lookup or ends in a 500.
7. Contract drift. Responses that don't match their declared schema, and clients that read fields the schema doesn't have.
8. Stale client cache. Mutations that don't refresh the data they change, and state derived from props or queries that isn't reset when they change.
9. Swallowed errors. Errors caught and logged where the caller needs the failure.
10. Half-finished changes. A recent dependency bump or change whose effect wasn't followed through everywhere it reaches.

A suspicion is not a bug. Code you merely find unusual is not a bug.

## Evidence

Write a regression test that reproduces the bug. Run it on the unchanged code and confirm it fails, then apply the fix and confirm it passes. Include both test outputs in the issue and PR. If you cannot write a failing test, the bug is not proven: call `noop`.
