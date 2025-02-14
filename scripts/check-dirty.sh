#!/usr/bin/env bash
set -e

if [[ -z "$(git status --porcelain)" ]];
then
  exit 0
else
  echo "Git is dirty"
  echo $(git status --porcelain)
  echo $(git diff)

  exit 1
fi
