#!/usr/bin/env bash
[[ -x ${VIRTUAL_ENV:-}/bin/mypy ]] || VIRTUAL_ENV=backend/.venv
[[ -x $VIRTUAL_ENV/bin/mypy ]] || { echo "mypy not found in $VIRTUAL_ENV: run poetry install --all-groups in backend/." >&2; exit 1; }
exec "$VIRTUAL_ENV/bin/mypy" "$@"
