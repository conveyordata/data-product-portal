# Domain docs

Single context. Skills that mention `GLOSSARY.md` mean `CONTEXT.md` in this repo.

- Glossary: `CONTEXT.md` at the repo root. Use its terms; add resolved terms there. Never create `GLOSSARY.md`.
- ADRs: `docs/adr/`, numbered `NNNN-title.md`. Write and revise them with the `adr` skill (`.claude/skills/adr/`) and `docs/adr/0000-template.md`, not a generic ADR format.

Before exploring an area, read the ADRs that touch it. If your output contradicts an ADR, say so explicitly instead of silently overriding it.
