# Issue tracker: GitHub

Issues for this repo live in GitHub Issues (`conveyordata/data-product-portal`). Use the `gh` CLI.

- Create: `gh issue create --title "..." --body "..." --label bug|enhancement`
- Read: `gh issue view <number> --json number,title,body,labels,comments`
- List: `gh issue list --state open --label <label>`
- Comment: `gh issue comment <number> --body "..."`
- Labels: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- Sub-issue: `gh issue create --parent <parent> ...`
- Close: `gh issue close <number> --comment "..."`

PRs as a request surface: no.

When a skill says "publish to the issue tracker", create a GitHub issue. When it says "fetch the relevant ticket", read it as above.
