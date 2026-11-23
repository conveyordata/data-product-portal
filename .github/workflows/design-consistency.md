---
name: "Background agent: Design consistency"
description: Finds the biggest visual inconsistency in the UI and aligns it, with before and after screenshots
on:
  schedule: weekly on thursday
  skip-if-match: 'is:open label:agent-design-consistency'
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 90
runs-on: ubuntu-24.04
sandbox:
  agent:
    runtime: docker-sudo-iptables
imports:
  - shared/background-agent.md
network:
  allowed:
    - playwright
tools:
  playwright:
safe-outputs:
  report-failure-as-issue: false
  create-issue:
    title-prefix: "[design consistency] "
    labels: [background-agent, agent-design-consistency]
    expires: false
  create-pull-request:
    draft: false
    title-prefix: "[design consistency] "
    labels: [background-agent, agent-design-consistency]
    github-token-for-extra-empty-commit: none
  upload-asset:
    allowed-exts: [.png]
    max: 20
  noop:
    report-as-issue: false
---

# Design consistency

Find the biggest visual inconsistency a user of the portal would notice, and align it. This is about what the UI looks like, not how the code is written.

Read `.claude/skills/portal-design/SKILL.md` first: it is the portal's design guide, and every finding must break one of its rules. Name that rule in the issue.

## Required survey

Start the app before deciding anything; a survey without screenshots is not a survey. Use one viewport (1440×900). Screenshot each screen below with the sample data, and compare the screens that belong to the same family side by side. Paths are in `frontend/src/types/navigation.ts`.

Screen families:
- Detail pages: a Data Product, an Output Port, a Technical Asset and an Exploration (each with its tabs).
- Create and edit: new and edit Data Product, new and edit Technical Asset, edit Output Port, edit Exploration, and the Output Port create dialog.
- Lists: Product Studio, Marketplace, People, every Settings tab, the Roles page, and the tables inside the detail tabs.
- Home, the Marketplace cart, and the notification and pending-request lists.

Checks (each names the `portal-design` section it enforces):
1. Detail page shell (§3): header, edit button, sidebar width and parent context are the same on all four detail pages, as `components/detail-page-layout/` draws them.
2. Create and edit flows (§5): page or modal, title, breadcrumb, and footer button order and labels, against new and edit Data Product.
3. Icons (§6): a table of icon to meaning across the screens. One icon with two meanings, one meaning with two icons, and icon-only actions without a tooltip.
4. Tables and empty states (§5): `size="small"`, total and pagination at the top right, action column last, and `EmptyState` or `ListTable` empty states, on every list screen.
5. Statuses (§4): each status of an object shows the same colour, icon and label on every screen it appears on.
6. Sibling cards and tiles (§8): equal width, title size and text hierarchy, and icons aligned and the same size.
7. Colour (§9): colours that are not theme tokens, and black next to coloured primary buttons.
8. Copy (§7): visible terms that `CONTEXT.md` lists under _Avoid_, and the same action labelled differently ("Add" against "New", casing).
9. Buttons (§5): placement of edit, add, save and delete, text or icon, and row actions in compact lists as `type="link" size="small"` without an icon.
10. Spacing (§5, §8): gaps between page sections and between cards in the same family.

The target is what the design guide prescribes and most equivalent screens already do, implemented the way `frontend/AGENTS.md` prescribes. Never introduce a new visual style. Rules in the guide that need new flows or features (guided tours, new pages) are out of scope: fix inconsistencies only.

## Run the app

Start the portal locally with sample data so you can look at it:

1. Backend: from `backend/`, with the values from `backend/.test.env`, `POSTGRES_SERVER=host.docker.internal` and `CORS_ALLOWED_ORIGINS=http://localhost:3000`, run `.venv/bin/python -m app.db_tool init --force sample_data.sql`, then start the API on port 5050 in the background as `backend/README.md` describes.
2. Frontend: from `frontend/`, copy `config.docker.js` to `config.local.js`, then run `npm run dev` in the background.

If the commands have changed, follow `backend/README.md` and `frontend/package.json` instead. Browse the pages with Playwright on `localhost`.

## Evidence

Take screenshots of every affected screen before the change and after it, at the same viewport and state. Upload them with `upload_asset` and put them side by side in the issue and in the PR body, as the PR description skill describes. Existing tests and pre-commit must pass.
