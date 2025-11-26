#!/usr/bin/env bash

set -ex

pushd backend
  cat .test.env
  poetry run python -m app.open_api_export ../docs/static/openapi.json
popd

#!/usr/bin/env bash
set -e

if [[ -z "$(git status --porcelain docs/static/openapi.json)" ]];
then
  exit 0
else
  echo "Git is dirty"
  git status --porcelain docs/static/openapi.json
  git --no-pager diff
  exit 1
fi
