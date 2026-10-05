---
name: pr-description
description: Writes pull request descriptions focused on the big picture - what changes functionally, why, whether it is reversible, a visual of the change, and UI screenshots. Use when creating a PR, writing a PR description, or summarizing a branch for reviewers.
---

# PR description

Describe the change for a reviewer who has not seen the code. Stay at the big picture: no file-by-file or line-level walkthroughs, the diff already shows those.

## Gather

1. `git log main..HEAD` and `git diff main...HEAD --stat` to see what the branch does.
2. Read the diff only as far as needed to understand the functional change.
3. Look for a linked issue or the notion page provided, you can ask the user for that or ADR (`docs/adr/`) for the context.

## Structure

```markdown
## What changes
<What a user, operator or integrator notices after merge. 2-5 bullets, in the domain language from CONTEXT.md.>

## Why
<One or two sentences. Link the issue or ADR if there is one.>

## One-way or two-way door
<Two-way door: easy to revert (UI, behaviour behind existing APIs).
One-way door: hard to undo (database migrations that drop or reshape data, public API or SDK contract changes, data written in a new format).
State which, and for a one-way door say what makes it hard to reverse.>

## Visual
<One diagram of the change, see below.>

## Screenshots
<Only when the UI changed, see below.>

## Checklist
<Copy the items from .github/PULL_REQUEST_TEMPLATE.md.>
```

Drop a section only when it truly has nothing to say (Screenshots for a backend-only PR). Keep the whole description short enough to read in a minute.

## Visual

Follow the formats in `.claude/skills/show-me/SKILL.md` and pick the single smallest one that shows the change: a Mermaid sequence or flow diagram for new interactions, a `diff`-style component, call or file tree for structural changes, a state diagram for lifecycle changes. Keep it big picture, use real names, and leave out anything that does not help the reviewer understand the change. GitHub renders Mermaid in PR descriptions; do not produce an HTML file.

## Screenshots

If the PR touches `frontend/` in a way the user can see, add screenshots, ideally before (on `main`) and after (on the branch) side by side:

```markdown
| Before | After |
| --- | --- |
| <screenshot> | <screenshot> |
```

If you can run the app and capture them, do so. Otherwise leave `<!-- TODO: screenshot of ... -->` placeholders naming the exact page and state to capture, and tell the author they still need to add them (images are uploaded through the GitHub web UI).
