---
name: "Background agent: Frontend consistency"
description: Finds the biggest code inconsistency in the frontend and aligns it to the dominant pattern
on:
  schedule: weekly on tuesday
  skip-if-match: 'is:open label:agent-frontend-consistency'
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
    title-prefix: "[frontend consistency] "
    labels: [background-agent, agent-frontend-consistency]
    expires: false
  create-pull-request:
    draft: false
    title-prefix: "[frontend consistency] "
    labels: [background-agent, agent-frontend-consistency]
    github-token-for-extra-empty-commit: none
  noop:
    report-as-issue: false
---

# Frontend code consistency

Find the biggest inconsistency in how the frontend code does the same thing in different ways, and align it to one pattern.

The target pattern is the one the documents below prescribe; if they say nothing, the one most of the codebase already uses. Never introduce a new pattern.

## What to hold the code to

The rules in `AGENTS.md`, `frontend/AGENTS.md` and `.claude/skills/portal-design/SKILL.md`, and the terms in `CONTEXT.md`. Go through them section by section, and compare code that does the same job side by side: forms, pages, detail pages, lists, and tabs with the same name under different entities.

## Kinds of defect to look for

Examples, not a complete list:

1. The same part of a screen (form footer, page shell, header, list, empty state) built in different ways instead of one way or a shared component.
2. The same action worded, ordered or confirmed differently between siblings.
3. One icon with two meanings, or one meaning with two icons.
4. Raw colours, sizes and spacing instead of theme tokens, and deprecated library values.
5. Terms `CONTEXT.md` lists under _Avoid_ in copy or identifiers.
6. Dead code: styles, components, props or translations nothing uses, and references to ones that don't exist.
7. Data fetching, loading and error states, routing and enums handled differently from the written rules.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. Existing tests and pre-commit must pass. For any visible change, add before and after screenshots as described in the PR description skill.
