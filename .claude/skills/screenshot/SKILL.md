---
name: screenshot
description: Screenshots portal pages from the running dev app, optionally next to the same pages on main. Use before handing over a UI change, to check a layout yourself, or for the before/after screenshots of a PR description.
---

# Screenshot

Look at your own UI change before the user does. A side-by-side with main catches regressions you did not mean to make, such as spacing that moved on a page you only touched indirectly.

## Steps

1. Make sure the dev app runs: frontend on `localhost:3000` and backend on `localhost:5050` with `OIDC_ENABLED=false`, so every page opens as the sample user John without a login. The frontend must run from the checkout that holds your change.
2. Run, from the repository:

   ```bash
   .claude/skills/screenshot/screenshot.sh --compare main <out-dir> home studio marketplace
   ```

   - A page is a name (`home` is `/`, any other name is `/<name>`) or `name=/path?tab=...` for a deeper page, for example `announcements=/marketplace/<data-product-id>/datasets/<output-port-id>?tab=announcements`.
   - Without `--compare`, it only screenshots your version. With `--compare <ref>`, it also serves the frontend of `<ref>` on port 3001 against the same backend and writes `<name>.<ref>.png` next to `<name>.png`.
   - Use your scratchpad as `<out-dir>`, never the repository.
   - Viewport is 1440x1300, full page. The first run downloads Playwright; if Chromium is missing, run `npx playwright@1.56.0 install chromium`.
3. Read every screenshot pair. Each difference must be one you intended; fix the others before you hand over.

Completion: every page your change can affect has been looked at next to main, and every difference is intended.

## States the URL cannot reach

For a popover, modal or hover state, write a short Playwright script in your scratchpad that opens the page and clicks to the state. Two gotchas:

- Use `exact: true` on role names: `getByRole('button', { name: 'Acknowledge' })` also matches "Acknowledge all".
- Clicks change the dev database (acknowledged notifications, deleted rows). Tell the user what you changed, or restore it, before they look at the app.
