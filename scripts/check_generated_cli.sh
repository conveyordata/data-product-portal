#!/usr/bin/env bash
set -e

# Check if the generated API is up to date
cd cli/golang

echo "Checking if generated CLI is up to date..."

# Run generate-api
go generate ./...

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

echo "✅ Generated CLI files are up to date."
