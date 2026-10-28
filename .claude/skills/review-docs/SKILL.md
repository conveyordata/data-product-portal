---
name: review-docs
description: 'Reviews written documentation for clarity, accuracy, consistency, and completeness; use when the user asks to review, proofread, or improve docs.'
---
## Documentation Review Workflow

When asked to review documentation, follow these steps in order.

### 1. Locate the docs

Identify the files to review — the user may specify a path, a PR diff, or a directory. If unclear, ask once.

Focus on `../../../docs` unless told otherwise. Skip versioned docs (e.g., `../../../docs/versioned_docs`).

### 2. Evaluate each document

Check each file against these criteria:

**Accuracy**
- Are all technical claims correct and up-to-date with the codebase?
- Do code examples actually work? Cross-check against source files when in doubt.
- Are referenced file paths, commands, and config keys correct?

**Clarity**
- Is the writing concise and free of jargon (or is jargon explained)?
- Are sentences short and active-voice where possible?
- Is the purpose of each section obvious from its heading?

**Consistency**
- Does terminology match the rest of the project docs and the UI/code?
- Is formatting consistent (headings, code blocks, lists)?
- Does writing style match the project's tone (check AGENTS.md for style notes)?

**Completeness**
- Are prerequisites stated?
- Are edge cases or failure modes mentioned where relevant?
- Are next-steps or related links provided?

**Structure**
- Is there a clear introduction, body, and conclusion (or next steps)?

### 3. Report findings

Group findings by severity:

- **Must fix** — factually wrong, broken commands, missing critical information.
- **Should fix** — unclear wording, inconsistent terminology, structural issues.
- **Consider** — minor style suggestions, optional improvements.

For each finding, include: file path, the problematic text (quoted), and a concrete suggestion.

### 4. Apply fixes (if asked)

If the user asks you to fix the issues (not just report them):
- Edit files directly with the edit tool.
- Make one focused change per issue — do not rewrite sections that are not flagged.
- After editing, re-read the changed section to verify it reads correctly.
- Do not add or remove content beyond what the finding calls for.

### Style guidelines for this project

- Don't overuse bold or italic — use them only for consistency with surrounding docs.
- Prefer short paragraphs and bullet lists over dense prose.
- Reference existing docs instead of duplicating content.
