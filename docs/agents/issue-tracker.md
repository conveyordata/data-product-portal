# Issue tracker: GitHub

Issues for this repo live in GitHub Issues (`conveyordata/data-product-portal`). Use the `gh` CLI.

- Create: `gh issue create --title "..." --body "..." --label bug|enhancement`
- Read: `gh issue view <number> --json number,title,body,labels,comments`
- List: `gh issue list --state open --label <label>`
- Comment: `gh issue comment <number> --body "..."`
- Labels: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- Sub-issue: `gh issue create --parent <parent> ...` (gh 2.94+). On older gh, put `Part of #<parent>` at the top of the child body.
- Close: `gh issue close <number> --comment "..."`

PRs as a request surface: no.

When a skill says "publish to the issue tracker", create a GitHub issue. When it says "fetch the relevant ticket", read it as above.

## Wayfinding operations

- Map: one issue labelled `wayfinder:map`.
- Ticket: a sub-issue of the map, labelled `wayfinder:<research|prototype|grilling|task>`.
- Blocking: a `Blocked by: #<n>, #<n>` line at the top of the ticket body. A ticket is unblocked when every blocker is closed.
- Frontier: open sub-issues of the map without an open blocker or an assignee, first in map order.
- Claim: `gh issue edit <n> --add-assignee @me` before any other work.
- Resolve: comment the answer, close the issue, add a one-line gist with link to the map's Decisions so far.
