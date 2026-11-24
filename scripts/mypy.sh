#!/usr/bin/env bash
[[ -x ${VIRTUAL_ENV:-}/bin/mypy ]] || VIRTUAL_ENV=backend/.venv
exec "$VIRTUAL_ENV/bin/mypy" "$@"
