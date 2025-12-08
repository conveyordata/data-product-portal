#!/usr/bin/env bash

set -ex

pushd backend
  set -a
  source .test.env
  set +a
  poetry run python -m app.open_api_export ../docs/static/openapi.json
popd

set -e

# Check only for unstaged changes (working directory differs from index)
if [[ -z "$(git diff docs/static/openapi.json)" ]];
then
  exit 0
else
  echo "Git is dirty"
  git status --porcelain docs/static/openapi.json
  git --no-pager diff docs/static/openapi.json
  exit 1
fi
