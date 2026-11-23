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

The target pattern is the one `frontend/AGENTS.md` or `.claude/skills/portal-design/SKILL.md` prescribes, or the canonical sibling named below; if none says anything, the one most of the codebase already uses. Never introduce a new pattern.

## Required survey

Read `frontend/AGENTS.md` and `.claude/skills/portal-design/SKILL.md`, then go through the checks below. Count each variant separately: `middle` and `medium` are two variants, not one.

Sibling families to compare side by side. Read the files, don't only grep:
- Create and edit forms: `frontend/src/components/data-products/data-product-form/`, `components/output-ports/output-port-form/`, `components/explorations/exploration-form/`, `components/data-products/technical-asset-form/`, `pages/technical-asset-edit/technical-asset-form/`.
- Create and edit pages: `pages/*-create/*.page.tsx`, `pages/*-edit/*.page.tsx`, and any create form rendered inside a modal.
- Detail pages: `pages/{data-product,output-port,technical-asset,exploration}/*.page.tsx`.
- Tabs with the same name under different entities (`pages/*/components/*-tabs/*`) and the settings tables (`pages/settings/components/settings-tabs/components/*-table/`).

Checks:
1. Form footer. Canonical: `data-product-form.component.tsx`. Delete on the left (edit only), then Cancel and the primary submit on the right; the submit says "Save" when editing and "Create" when creating. Flag any other order, label or layout, and any delete confirmation whose wording differs from the majority.
2. Create and edit page shell: where the title and breadcrumbs are set, extra wrappers or SCSS, and a modal versus a page for creating a core entity.
3. Detail pages use `DetailPageLayout`; flag any page that builds its own header, edit button or sidebar.
4. Icons: build an icon-to-meaning table from `@ant-design/icons` usages and their tooltips or labels. Flag one icon with two meanings and one meaning with two icons.
5. Lists: `<Table` and `<Empty` outside `components/list-table/` and `components/empty-state/`. Tables inside forms and selectors are exempt.
6. Duplicated UI: files in the sibling families that repeat the same structure instead of sharing one component from `frontend/src/components/`.
7. Tokens: hex colours and `px` values in `*.scss` and inline `style`, numeric gaps, and deprecated Ant Design values.
8. Copy: `t('…')` strings that use a term `CONTEXT.md` replaces, for example "Dataset" instead of Output Port.
9. Dead styling: `styles.X` references to a class the imported module does not define, and empty `.module.scss` files.
10. Data fetching, loading and error states, routing, i18next, and enums versus plain strings, as `frontend/AGENTS.md` prescribes.

## Evidence

In the issue and PR, show the count of usages of each variant before and after, with a few representative file references, and cite the AGENTS.md rule or the dominant usage that justifies the target. Existing tests and pre-commit must pass. For any visible change, add before and after screenshots as described in the PR description skill.
