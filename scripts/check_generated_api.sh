#!/usr/bin/env bash
set -e

# Check if the generated API is up to date
cd frontend

echo "Checking if generated API is up to date..."

# Run generate-api
npm run generate-api

if [[ -n "${CI}" ]]; then
  if [[ -z "$(git status --porcelain src/store/api/services/generated)" ]];
  then
    exit 0
  else
    echo "Git is dirty"
    git status --porcelain src/store/api/services/generated
    git --no-pager diff
    exit 1
  fi
fi

echo "✅ Generated API files are up to date."
