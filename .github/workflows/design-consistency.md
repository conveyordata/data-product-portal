---
description: Finds the biggest visual inconsistency in the UI and aligns it, with before and after screenshots
on:
  schedule: weekly on thursday
  skip-if-match: 'is:open label:agent-design-consistency'
permissions:
  contents: read
  issues: read
  pull-requests: read
  copilot-requests: write
timeout-minutes: 90
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
  create-issue:
    title-prefix: "[design consistency] "
    labels: [background-agent, agent-design-consistency]
    expires: false
  create-pull-request:
    title-prefix: "[design consistency] "
    labels: [background-agent, agent-design-consistency]
  upload-asset:
    allowed-exts: [.png]
    max: 20
  noop:
    report-as-issue: false
---

# Design consistency

Find the biggest visual inconsistency a user of the portal would notice, and align it. This is about what the UI looks like, not how the code is written.

Read `.claude/skills/portal-design/SKILL.md` first: it is the portal's design guide, and every finding must break one of its rules. Name that rule in the issue.

Compare equivalent elements across pages: padding, margins and gaps; font sizes and weights; page and section titles (wording, level, placement); the icon used for the same concept or action; the label used for the same action or domain term; button order, type and placement; alignment of headers, tables, forms and cards; empty, loading and error states; status colours, icons and labels; and how the same entity (Data Product, Output Port, ...) is shown in different places.

The target is what the design guide prescribes and most equivalent screens already do, implemented the way `frontend/AGENTS.md` prescribes. Never introduce a new visual style. Rules in the guide that need new flows or features (guided tours, new pages) are out of scope: fix inconsistencies only.

## Run the app

Start the portal locally with sample data so you can look at it:

1. Backend: from `backend/`, with the values from `backend/.test.env`, `POSTGRES_SERVER=host.docker.internal` and `CORS_ALLOWED_ORIGINS=http://localhost:3000`, run `poetry run python -m app.db_tool init --force sample_data.sql`, then start the API on port 5050 in the background as `backend/README.md` describes.
2. Frontend: from `frontend/`, copy `config.docker.js` to `config.local.js`, then run `npm run dev` in the background.

If the commands have changed, follow `backend/README.md` and `frontend/package.json` instead. Browse the pages with Playwright on `localhost`.

## Evidence

Take screenshots of every affected screen before the change and after it, at the same viewport and state. Upload them with `upload_asset` and put them side by side in the issue and in the PR body, as the PR description skill describes. Existing tests and pre-commit must pass.
