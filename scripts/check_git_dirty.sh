#!/usr/bin/env bash
set -e

if [[ -z "$(git status --porcelain)" ]];
then
  exit 0
else
  echo "Git is dirty"
  git status --porcelain
  git --no-pager diff
  exit 1
fi
