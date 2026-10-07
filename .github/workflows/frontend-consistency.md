---
description: Finds the biggest code inconsistency in the frontend and aligns it to the dominant pattern
on:
  schedule: weekly on tuesday
  skip-if-match: 'is:open label:agent-frontend-consistency'
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
  create-issue:
    title-prefix: "[frontend consistency] "
    labels: [background-agent, agent-frontend-consistency]
    expires: false
  create-pull-request:
    title-prefix: "[frontend consistency] "
    labels: [background-agent, agent-frontend-consistency]
  noop:
    report-as-issue: false
---

# Frontend code consistency

Find the biggest inconsistency in how the frontend code does the same thing in different ways, and align it to one pattern.

Examples of what to compare: raw pixel values versus semantic size tokens, hardcoded colours versus theme tokens, custom components that duplicate an existing shared component or an Ant Design one, different ways of fetching data, handling loading and error states, routing, forms and validation, hardcoded strings versus i18next, comparing against plain strings where an enum exists, and file and naming conventions.

The target pattern is the one `frontend/AGENTS.md` prescribes; if it says nothing, the one most of the codebase already uses. Never introduce a new pattern. Rank by how many places diverge and how much the divergence costs readers and maintainers. Keep the change reviewable: if the inconsistency is spread too wide for one PR, fix one coherent slice (for example one feature folder) and list the remaining places in the issue.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. Existing tests and pre-commit must pass. For any visible change, add before and after screenshots as described in the PR description skill.
