#!/bin/bash
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"

find "$REPO_ROOT" \
  -name "pyproject.toml" \
  -not -path "*/.venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/backend/*" \
  -not -path "*/sdk/*" \
  | while read -r toml; do
      dir="$(dirname "$toml")"
      if grep -q "\[tool\.mypy\]" "$toml"; then
          echo "--- mypy: $dir ---"
          (cd "$dir" && poetry run mypy .)
      fi
  done
