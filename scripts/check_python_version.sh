#!/usr/bin/env bash
set -uo pipefail

minor() { grep -m1 -oE '[0-9]+\.[0-9]+' | head -1; }

expected=$(grep -m1 -E '^requires-python = ' backend/pyproject.toml | minor)
if [[ -z "$expected" ]]; then
  echo "Could not read the Python version from backend/pyproject.toml"
  exit 1
fi

found=(
  "backend/.python-version|$(minor < backend/.python-version)"
  "Dockerfile|$(grep -m1 -oE 'python:[0-9]+\.[0-9]+' Dockerfile | minor)"
  "Taskfile.yml poetry:reqs|$(grep -m1 -oE 'requirements-poetry\.in .*--python-version [0-9]+\.[0-9]+' Taskfile.yml | grep -oE '[0-9]+\.[0-9]+$')"
  "plugins/pyproject.toml requires-python|$(grep -m1 -E '^requires-python = ' plugins/pyproject.toml | minor)"
  "plugins/pyproject.toml python|$(grep -m1 -E '^python = ' plugins/pyproject.toml | minor)"
)

status=0
for entry in "${found[@]}"; do
  if [[ "${entry#*|}" != "$expected" ]]; then
    echo "${entry%%|*} uses Python '${entry#*|}', backend/pyproject.toml requires $expected"
    status=1
  fi
done
exit $status
