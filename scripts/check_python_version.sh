#!/usr/bin/env bash
set -uo pipefail

minor() { grep -m1 -oE '[0-9]+\.[0-9]+'; }
hook() { sed -n "/name: mypy ($1)/,/- id:/p" .pre-commit-config.yaml | grep -m1 'language_version' | minor; }

expected=$(grep -m1 -E '^python = ' backend/pyproject.toml | minor)
if [[ -z "$expected" ]]; then
  echo "Could not read the Python version from backend/pyproject.toml"
  exit 1
fi

found=(
  "backend/.python-version|$(minor < backend/.python-version)"
  "Dockerfile|$(grep -m1 -oE 'python:[0-9]+\.[0-9]+' Dockerfile | minor)"
  "plugins/pyproject.toml requires-python|$(grep -m1 -E '^requires-python = ' plugins/pyproject.toml | minor)"
  "plugins/pyproject.toml python|$(grep -m1 -E '^python = ' plugins/pyproject.toml | minor)"
  "mypy (backend) hook|$(hook backend)"
  "mypy (plugins) hook|$(hook plugins)"
)

status=0
for entry in "${found[@]}"; do
  if [[ "${entry#*|}" != "$expected" ]]; then
    echo "${entry%%|*} uses Python '${entry#*|}', backend/pyproject.toml requires $expected"
    status=1
  fi
done
exit $status
