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

## Required survey

For each check, look for a concrete candidate and try to write a test that fails on the current code. The first candidate whose test fails is the bug you fix.

1. Enum name against value. Code, raw SQL rows and `backend/sample_data.sql` that compare or store an enum by `.name` where the column holds the `.value`, or the other way round. Compare sibling branches of the same function.
2. Visibility on writes. Updates and deletes that load or cascade through queries filtered by `app/database/visibility.py`, so rows the caller can't see are skipped or break the write.
3. Derived state that goes stale. Anything copied from a source of truth (authorization policies, events, graph nodes and edges, counts, cached flags) that is not updated when the source is revoked, expired, renamed or deleted.
4. Time-bound access. Expiry and renewal in `abstract_data_product/input_ports/background_tasks.py` and `authorization/role_assignments/global_/background_tasks.py`: overlapping grants, revoke after renew, and expiry at the boundary.
5. Status transitions and guards. Approve, deny and revoke on pending, denied and expired states, and "last owner" style guards that count the wrong states.
6. Boundary validation. Names, ids, durations and config values accepted by the API that later break a lookup or a 500 path.
7. Response contract. Routes that return something other than their declared response schema, and frontend code that reads a field the OpenAPI schema does not have.
8. Frontend cache. RTK Query mutations in `frontend/src/store/api/services/tags/` whose `invalidatesTags` miss data the mutation changes, and component state derived from props or queries that is not reset when they change.
9. Swallowed errors. `except Exception` blocks that log and continue where the caller needs the failure.
10. Recent changes. Dependency bumps and merged PRs of the last month (`git log --since`) whose behaviour change was not followed through, as with the Tiptap 3 toolbar in #4717.

A suspicion is not a bug. Code you merely find unusual is not a bug.

## Evidence

Write a regression test that reproduces the bug. Run it on the unchanged code and confirm it fails, then apply the fix and confirm it passes. Include both test outputs in the issue and PR. If you cannot write a failing test, the bug is not proven: call `noop`.
