# Issue tracker: GitHub

Issues for this repo live in GitHub Issues (`conveyordata/data-product-portal`). Use the `gh` CLI.

- Create: `gh issue create --title "..." --body "..." --label bug` (use `enhancement` for features).
- Read: `gh issue view <number> --json number,title,body,labels,comments,closedByPullRequestsReferences`
- List: `gh issue list --state open --label <label>`
- Comment: `gh issue comment <number> --body "..."`
- Labels: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- Sub-issue: `gh issue create --parent <parent> ...` (gh 2.94+). On older gh, put `Part of #<parent>` at the top of the child body.
- Close: `gh issue close <number> --comment "..."`

PRs as a request surface: no.

When a skill says "publish to the issue tracker", create a GitHub issue. When it says "fetch the relevant ticket", read it as above.

## Wayfinding operations

`/wayfinder` never writes to GitHub. Its map and tickets are local scratch files, so research and small decisions don't turn into issues.

- Map: `.scratch/<effort>/map.md`.
- Ticket: `.scratch/<effort>/issues/NN-<slug>.md`, with a `Type:` line (`research`/`prototype`/`grilling`/`task`) and a `Status:` line (`open`/`claimed`/`resolved`, new tickets start `open`).
- Blocking: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every ticket it lists is `resolved`.
- Frontier: `Status: open` tickets that aren't blocked; lowest number first.
- Claim: set `Status: claimed` before any work.
- Resolve: append the answer under `## Answer`, set `Status: resolved`, add a one-line gist with link to the map's Decisions so far.

When the map settles a decision that is hard to reverse, propose turning it into an ADR. The user decides.
