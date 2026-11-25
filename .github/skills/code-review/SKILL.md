---
name: code-review
description: Review philosophy for GitHub Copilot code review comments - high-confidence, concise, actionable feedback.
---

## Review Philosophy
- Only comment when you have HIGH CONFIDENCE (>80%) that an issue exists
- Be concise: one sentence per comment when possible.
- Focus on actionable feedback, not observations
- When reviewing text, only comment on clarity issues if the text is genuinely confusing or could lead to errors.
- Before claiming a state is reachable, search the repo for the validator, database constraint or earlier migration that may rule it out. If you cannot verify it, don't comment.
- One comment per root cause. When the same mistake appears in several files, list the other locations in that one comment.
- Don't flag races or collisions that need improbable timing or input unless the result is data loss or a security hole. The backend can run as several replicas, so check-then-write races on normal requests are real.
- Look outside the diff where the change reaches: every read path a widened authorization or visibility rule opens, the seed files (`backend/sample_data.sql`, `demo/*/portal_seed.sql`) for a schema change, and "first match" lookups when discovery or ordering changes.
- If the PR description says it is stacked or that a follow-up PR adds the missing part, don't flag that part as missing.

## Project Conventions
Don't flag these, they are deliberate:
- Breaking changes ship in 0.x patch releases and are listed under breaking changes in the release notes.
- Plugin discovery fails fast on a broken plugin, and the plugin registry `get()` resolves plugins that are not enabled.

## PR Checklist
Only for PRs that change user-facing behaviour of a released feature. Skip it for fixes to unreleased work, internal endpoints, sample or demo data, small styling tweaks, and closed PRs. Check the diff before flagging an item. Flag each item that is missing, in the review summary only, never as an inline comment:
- User-facing behaviour changed but `docs/docs/` was not updated.
- User-facing change without an entry in `docs/docs/release-notes.md`.
- New entity or feature without matching data in `backend/sample_data.sql`, so reviewers cannot test it.
- UI changed but the PR description has no screenshots or videos.
