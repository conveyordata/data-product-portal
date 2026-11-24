# Bug list

Bugs found by the bug-finder background agent. It runs every Wednesday, adds what it finds as `open` and marks bugs `fixed` once they no longer happen. It never fixes them.

Triage in the pull request that adds them: change a risk, or set a row to `rejected` with the reason. Merging the pull request means the rows are triaged. Refer to a bug by its ID; when you take one up, link its issue or pull request in the row.

## Risk

- critical: data loss, a security or access leak, or the portal unusable.
- high: wrong behaviour on a common path, with no workaround.
- medium: wrong behaviour in an edge case, or there is a workaround.
- low: unlikely to happen, or minor impact.

## Status

- open: found and not fixed yet.
- rejected: not a bug, or not worth fixing. The reason is in the row.
- fixed: no longer happens. The row links the fix.

## Bugs

| ID | Bug | Where | Risk | Status | Found | Notes |
| --- | --- | --- | --- | --- | --- | --- |
