# Domain docs

Single context.

- Glossary: `GLOSSARY.md` at the repo root. Use its terms; add resolved terms there.
- ADRs: `docs/adr/`, numbered `NNNN-title.md`. Write and revise them with the `adr` skill (`.claude/skills/adr/`) and `docs/adr/0000-template.md`, not a generic ADR format. Propose an ADR when something hard to reverse is decided; only write it when the user says yes.

Before exploring an area, read the ADRs that touch it. If your output contradicts an ADR, say so explicitly instead of silently overriding it.
