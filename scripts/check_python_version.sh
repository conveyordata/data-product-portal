#!/usr/bin/env bash
set -euo pipefail

expected=$(grep -m1 -oE '^python = "\^[0-9]+\.[0-9]+' backend/pyproject.toml | grep -oE '[0-9]+\.[0-9]+')

found=(
  "backend/.python-version|$(grep -oE '^[0-9]+\.[0-9]+' backend/.python-version)"
  "Dockerfile|$(grep -m1 -oE 'python:[0-9]+\.[0-9]+' Dockerfile | cut -d: -f2)"
  "plugins/pyproject.toml requires-python|$(grep -m1 -oE '^requires-python = ">=[0-9]+\.[0-9]+' plugins/pyproject.toml | grep -oE '[0-9]+\.[0-9]+')"
  "plugins/pyproject.toml python|$(grep -m1 -oE '^python = "\^[0-9]+\.[0-9]+' plugins/pyproject.toml | grep -oE '[0-9]+\.[0-9]+')"
  "mypy (backend) hook|$(grep -A1 'name: mypy (backend)' .pre-commit-config.yaml | grep -oE 'python[0-9]+\.[0-9]+' | cut -c7-)"
  "mypy (plugins) hook|$(grep -A1 'name: mypy (plugins)' .pre-commit-config.yaml | grep -oE 'python[0-9]+\.[0-9]+' | cut -c7-)"
)

status=0
for entry in "${found[@]}"; do
  if [[ "${entry#*|}" != "$expected" ]]; then
    echo "${entry%%|*} uses Python '${entry#*|}', backend/pyproject.toml requires $expected"
    status=1
  fi
done
exit $status
