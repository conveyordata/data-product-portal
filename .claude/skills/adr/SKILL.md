---
name: adr
description: 'Drafts or reviews Architecture Decision Records in the project’s ADR format, using the repository template and examples to capture decisions, trade-offs, and outcomes.'
---

# ADR writing workflow

Use this skill when creating or revising an Architecture Decision Record (ADR) in this repository, especially when adding a new ADR under `docs/adr/` or updating an existing one.

## Project ADR conventions

Follow the project’s established ADR structure and tone:

- Start from `docs/adr/0000-template.md` as the canonical structure.
- Use examples in `docs/adr/` for style, level of detail, and expected sections.
- Prefer clear problem framing and explicit trade-off analysis over generic architecture prose.
- Write from the perspective of a concrete decision that was made, not a wishlist.

## Writing guidance

- Keep the ADR specific, evidence-based, and decision-oriented.
- Describe the trade-offs honestly: include costs, complexity, migration risk, and operational impact.
- Prefer concrete language like “breaking change,” “audit trail,” “access inheritance,” or “migration/backfill” when the decision affects real system behavior.
- Use a single decision question and avoid mixing unrelated concerns in one ADR.
- If a topic is still unresolved, add an `## Open Questions` section or call it out explicitly as a future follow-up.
- Keep the final answer readable by human reviewers and engineers who will implement the decision later.

## Good ADR checklist

Before finishing, verify:

- The title clearly names the decision.
- The problem statement is crisp and grounded in current context.
- The decision drivers are explicit and relevant.
- The considered options are distinct and realistic.
- The chosen option is clearly identified and justified.
- The consequences are weighed with pros/cons.
- The ADR reads like a stable record of a real decision, not a design note or brainstorming document.

## Workflow for drafting an ADR

1. Identify the decision, the problem, and the deadline or trigger for the ADR.
2. Write the context and problem statement in 1–3 paragraphs.
3. List 3–6 decision drivers, grounded in business or technical realities.
4. Enumerate realistic options without inventing unrealistic alternatives.
5. Choose the preferred option and explain the reasoning.
6. Add the confirmation section describing the implementation implications.
7. Review the ADR for clarity, completeness, and consistency with the repository’s prior ADRs.
8. Save it in `docs/adr/` with the project’s naming convention and ensure the file is well-structured and readable.

## Reference examples

Use these as the main style references:

- `docs/adr/0000-template.md` — base structure
- `docs/adr/0010-improve-search.md` — concise but decision-focused ADR with an explicit chosen option and confirmation section
- `docs/adr/0014-slow-queries.md` — shorter ADR that is practical and implementation-aware, with appendices when useful
- `docs/adr/0017-versioning.md` — long-form reasoning, clear drivers, detailed option comparisons
- `docs/adr/0021-input-ports-and-input-port-requests.md` — concrete design details and confirmation section

These examples show that ADRs in this repo do not all need to be equally long or formal. The key pattern is consistent: state the problem clearly, list the drivers, compare realistic options, explain the decision, and make the trade-offs visible.
