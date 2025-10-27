#!/usr/bin/env bash

set -ex

pushd backend
  cat .test.env
  poetry run python -m app.open_api_export ../docs/static/openapi.json
popd

./scripts/check_git_dirty.sh
