---
name: code-review
description: 'Reviews a pull request diff for the problems reviewers in this repository keep finding by hand; use when reviewing a PR, before approving or requesting changes.'
---

Ruff, mypy, Biome and the pre-commit hooks already cover formatting, typing,
lint rules and the generated clients. `AGENTS.md` and `backend/AGENTS.md` already
cover layering, Pydantic v2, SQLAlchemy loading, authorization and test naming.
Do not raise any of that.

Raise these, most frequently missed first.

## Every non-obvious change says why

A moved import, a new setting, a workaround, an unusual default. The reason
belongs in the pull request description or the commit message, not in a code
comment. If you find yourself asking "why is this here", the author should
already have answered it.

## Nothing exists for a future that has not arrived

A new flag, parameter, subclass or abstraction needs something that needs it
today. One caller and no concrete second use case is worth raising. A setting
added only to quiet test noise is the usual shape.

## Something already does this

Before accepting hand-written logic, look for an existing helper in the repo, a
library function, a native CSS or HTML feature, or a stdlib decorator. Recurring
misses: CSS instead of JavaScript layout code, a date library instead of manual
arithmetic, `functools.cache`, `Form.useForm()`.

## A rename reaches every use of the old name

Test names, error messages, docstrings, docs, fixtures, demo code, other
packages in the repository. Search for the old name before approving.

## Assertions have to be able to fail

A test that asserts a constant against itself, or asserts a value the fallback
path also produces, passes whether or not the feature works. Ask what change
would make each new test fail.

## Code outside backend/ and frontend/ still has to work

`demo/`, `cli/`, `sdk/` and `integrations/` are not covered by the test suite.
When a shared model, generated client or public name changes, check whether
those directories still import and run.
