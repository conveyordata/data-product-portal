#!/usr/bin/env bash
[[ -x ${VIRTUAL_ENV:-}/bin/mypy ]] || VIRTUAL_ENV=backend/.venv
[[ -x $VIRTUAL_ENV/bin/mypy ]] || VIRTUAL_ENV=$(cd backend && poetry env info -p 2>/dev/null)
[[ -x $VIRTUAL_ENV/bin/mypy ]] || { echo "mypy not found in the backend environment: run poetry install --all-groups in backend/." >&2; exit 1; }
exec "$VIRTUAL_ENV/bin/mypy" "$@"
