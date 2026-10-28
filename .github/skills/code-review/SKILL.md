---
name: code-review
description: Review philosophy for GitHub Copilot code review comments - high-confidence, concise, actionable feedback.
---

## Review Philosophy
- Only comment when you have HIGH CONFIDENCE (>80%) that an issue exists
- Be concise: one sentence per comment when possible.
- Focus on actionable feedback, not observations
- When reviewing text, only comment on clarity issues if the text is genuinely confusing or could lead to errors.

## PR Checklist
Flag each item that is missing, in one top-level comment:
- User-facing behaviour changed but `docs/docs/` was not updated.
- User-facing change without an entry in `docs/docs/release-notes.md`.
- New entity or feature without matching data in `backend/sample_data.sql`, so reviewers cannot test it.
- UI changed but the PR description has no screenshots or videos.
