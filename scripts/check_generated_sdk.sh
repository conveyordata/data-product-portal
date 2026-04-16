#!/usr/bin/env bash
set -e

# Check if the generated API is up to date

echo "Checking if generated SDK is up to date..."
pushd sdk


  # Install dependencies (including openapi-python-client)
  poetry install --no-interaction --only dev
  
  # Run generate-api
  poetry run openapi-python-client generate \
    --path ./../docs/static/openapi.json \
    --output-path ./sdk/api_client \
    --meta none \
    --overwrite


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

popd
echo "✅ Generated API files are up to date."
