---
applyTo: "frontend/**"
---

# Demo frontend changes with screenshots

When you change user-facing behaviour in the frontend, show that it works in the running app before finishing.

## Start the app

```sh
cd backend
cp .test.env .env
poetry run python -m app.db_tool init --force "sample_data.sql"
poetry run python -m app.local_startup &   # API on http://localhost:5050

cd ../frontend
npm run dev &                              # UI on http://localhost:3000
```

OIDC is disabled in both configs, so no login is needed.

## Capture the walkthrough

Use the Playwright browser tool against http://localhost:3000:

1. Navigate to the screen you changed, starting from the home page.
2. Take a screenshot at each meaningful step of the flow, including the final result.
3. If the change affects an error or empty state, capture that too.

## Report in the PR description

Add a `## Demo` section to the PR description with a numbered list, one entry per step:

- one sentence saying what was done (e.g. "Open a data product and click Edit")
- the screenshot for that step

Skip this for changes with no visible effect (refactors, tests, types only).
