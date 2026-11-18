---
name: screenshot
description: Screenshots portal pages from the running dev app, optionally next to the same pages on main. Use before handing over a UI change, to check a layout yourself, or for the before/after screenshots of a PR description.
---

# Screenshot

Look at your own UI change before the user does. A side-by-side with main catches regressions you did not mean to make, such as spacing that moved on a page you only touched indirectly.

## Steps

1. Make sure the dev app runs: frontend on `localhost:3000` and backend on `localhost:5050` with `OIDC_ENABLED=false`, so every page opens as the sample user John without a login. The frontend must run from the checkout that holds your change.
   - Check for a listener first with `lsof -nP -iTCP:3000 -sTCP:LISTEN -t` and its folder with `lsof -a -p <pid> -d cwd`. The user often has their own dev server there: reuse it when it runs from your checkout's `frontend/` and pages open as John, and leave it running. When it runs from another checkout, stop and ask the user; that server is theirs.
   - When port 3000 is free, start your own from `frontend/` with `npm run dev -- --strictPort`, so Vite fails instead of moving to another port. Record the PID listening on 3000 (the `vite` process, not `npm`, which leaves Vite running when killed) and confirm its folder is your checkout.
   - Afterwards, stop exactly that recorded PID with `kill <pid>`.
2. Run, from the repository:

   ```bash
   .claude/skills/screenshot/screenshot.sh --compare main --width 1200 --width 1280 --width 1440 <out-dir> home studio marketplace
   ```

   - A page is a name (`home` is `/`, any other name is `/<name>`) or `name=/path?tab=...` for a deeper page, for example `announcements=/marketplace/<data-product-id>/datasets/<output-port-id>?tab=announcements`.
   - Without `--compare`, it only screenshots your version. With `--compare <ref>`, it also serves the frontend of `<ref>` on port 3001 against the same backend and writes `<name>.<ref>.png` next to `<name>.png`.
   - The viewport is 1440 wide by default. Each `--width <px>` replaces that default with the widths you list, written as `<name>-<width>.png`. Layout bugs show between 1200 (the app's minimum width) and 1440, so shoot a layout change at all three.
   - A page whose layout scrolls sideways (the document, `#root` or the page content area) prints `OVERFLOW <px>` after its file name. Tables that scroll inside themselves do not count.
   - Use your scratchpad as `<out-dir>`, never the repository.
   - Screenshots are full page, 1300 high. The first run downloads Playwright; if Chromium is missing, run `npx playwright@1.56.0 install chromium`.
3. Read every screenshot pair. Each difference must be one you intended; fix the others before you hand over.

Completion: every page your change can affect has been looked at next to main, every difference is intended, and no page you changed prints `OVERFLOW`.

## States the URL cannot reach

For a popover, modal or hover state, write a short Playwright script in your scratchpad that opens the page and clicks to the state. Two gotchas:

- Use `exact: true` on role names: `getByRole('button', { name: 'Acknowledge' })` also matches "Acknowledge all".
- Clicks change the dev database (acknowledged notifications, deleted rows). Tell the user what you changed, or restore it, before they look at the app.
