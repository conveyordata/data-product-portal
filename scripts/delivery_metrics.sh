#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-conveyordata/data-product-portal}"
MONTHS="${MONTHS:-6}"
SINCE=$(date -u -d "-${MONTHS} months" +%Y-%m-01 2>/dev/null || date -u -v-"${MONTHS}"m +%Y-%m-01)

prs=$(gh pr list -R "$REPO" --state all --limit 2000 \
  --search "updated:>=$SINCE -author:app/dependabot" \
  --json author,state,createdAt,mergedAt,reviews)
bugs=$(gh issue list -R "$REPO" --state all --limit 1000 --label bug \
  --search "created:>=$SINCE" --json body)
threads=$(gh api graphql --paginate -f query='
query($endCursor: String) {
  search(query: "repo:'"$REPO"' is:pr is:merged merged:>='"$SINCE"'", type: ISSUE, first: 50, after: $endCursor) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on PullRequest { reviewThreads(first: 100) { nodes {
      isResolved isOutdated
      comments(first: 1) { nodes { author { login } createdAt reactionGroups { content reactors { totalCount } } } }
    } } } }
  }
}' --jq '.data.search.nodes[].reviewThreads.nodes[]
  | select(.comments.nodes[0].author.login == "copilot-pull-request-reviewer")' | jq -s .)
releases=$(gh release list -R "$REPO" --limit 100 --json tagName,publishedAt \
  --jq "[.[] | select(.publishedAt >= \"$SINCE\")]")

printf '%s\n' "$prs" "$bugs" "$releases" "$threads" | jq -rn --arg since "$SINCE" '
def hours(a; b): ((b | fromdate) - (a | fromdate)) / 3600;
def median: sort | length as $n | if $n == 0 then null elif $n % 2 == 1 then .[$n / 2 | floor] else (.[$n / 2 - 1] + .[$n / 2]) / 2 end;
def fmt: if . == null then "-" else (. * 10 | round / 10 | tostring) end;
def agent: .author.login | test("copilot|claude"; "i");
def first_review: [.reviews[] | select(.author.login | test("copilot"; "i") | not) | .submittedAt] | min;

(input) as $prs | (input) as $bugs | (input) as $releases | (input) as $threads
| ($since[0:7]) as $first
| ($prs | map(select(.createdAt[0:7] >= $first) | . + {month: .createdAt[0:7]})) as $opened
| ($prs | map(select(.mergedAt and .mergedAt[0:7] >= $first) | . + {month: .mergedAt[0:7]})) as $merged
| ([$opened[].month, $merged[].month] | unique | map(. as $m
  | ($opened | map(select(.month == $m))) as $o
  | ($merged | map(select(.month == $m))) as $g
  | {
    month: $m,
    opened: ($o | length),
    merged: ($g | length),
    lead: ($g | map(hours(.createdAt; .mergedAt)) | median),
    review: ($o | map(select(first_review) | hours(.createdAt; first_review)) | median),
    agent_opened: ($o | map(select(agent)) | length),
    agent_merged: ($g | map(select(agent)) | length)
  })) as $rows
| ($threads | map(.comments.nodes[0] as $c
    | ($c.reactionGroups | map({(.content): .reactors.totalCount}) | add) as $r
    | {month: $c.createdAt[0:7], signal: (
        if $r.THUMBS_UP > 0 then "up"
        elif $r.THUMBS_DOWN > 0 then "down"
        elif .isOutdated then "acted"
        elif .isResolved then "dismissed"
        else "none" end)})
  | group_by(.month) | map(. as $g | {month: $g[0].month, total: length}
    + (["up", "down", "acted", "dismissed", "none"] | map(. as $s | {($s): ([$g[] | select(.signal == $s)] | length)}) | add))) as $review
| ($bugs | map(.body | (capture("### Found in version\\s+v?(?<v>[0-9][^\\s]*)")? | .v)) | map(select(.))) as $found
| ($releases | map(.tagName | ltrimstr("v")) | map(. as $v | {v: $v, bugs: ($found | map(select(. == $v)) | length)})) as $rel
| "# Delivery metrics",
  "",
  "Since \($rows[0].month), excluding Dependabot. Updated \(now | todate[0:10]). Opened and first review count by month opened; merged and lead time by month merged.",
  "",
  "| Month | PRs opened | Merged | Median lead time (h) | Median first human review (h) | Agent PRs opened | Agent PRs merged |",
  "|---|---|---|---|---|---|---|",
  ($rows[] | "| \(.month) | \(.opened) | \(.merged) | \(.lead | fmt) | \(.review | fmt) | \(.agent_opened) | \(.agent_merged) |"),
  "",
  "```mermaid",
  "xychart-beta",
  "  title \"Median hours per month (bar: lead time, line: first human review)\"",
  "  x-axis [\($rows | map("\"" + .month + "\"") | join(", "))]",
  "  y-axis \"Hours\"",
  "  bar [\($rows | map(.lead // 0 | round) | join(", "))]",
  "  line [\($rows | map(.review // 0 | round) | join(", "))]",
  "```",
  "",
  "## Copilot review usefulness",
  "",
  "Copilot review comments on merged PRs. A 👍 or 👎 reaction wins; otherwise \"acted on\" means the code on that line changed afterwards and \"dismissed\" means the thread was resolved without a change.",
  "",
  "| Month | Comments | 👍 | 👎 | Acted on | Dismissed | No signal |",
  "|---|---|---|---|---|---|---|",
  ($review[] | "| \(.month) | \(.total) | \(.up) | \(.down) | \(.acted) | \(.dismissed) | \(.none) |"),
  "",
  "## Change failure rate",
  "",
  "Bugs reported against each release, from the \"Found in version\" field of the bug report form.",
  "",
  "| Release | Bugs found in it |",
  "|---|---|",
  ($rel[] | "| \(.v) | \(.bugs) |"),
  "",
  "Releases with at least one bug: \($rel | map(select(.bugs > 0)) | length) of \($rel | length)."
'
