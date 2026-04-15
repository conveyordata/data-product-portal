#!/usr/bin/env bash
set -e

# Check if the generated API is up to date
cd sdk

echo "Checking if generated API is up to date..."

# Run generate-api
task generate:client

if [[ -n "${CI}" ]]; then
  if [[ -z "$(git status --porcelain .)" ]];
  then
    exit 0
  else
    echo "Git is dirty"
    git status --porcelain .
    git --no-pager diff
    exit 1
  fi
fi

echo "✅ Generated API files are up to date."
