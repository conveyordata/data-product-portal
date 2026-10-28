#!/usr/bin/env bash
set -e

# Check if the generated SDK plugin configurations are up to date

echo "Checking if generated plugin configurations are up to date..."
pushd sdk

  poetry run python generation/build_plugin_configurations.py
  poetry run ruff format sdk/plugins
  poetry run ruff check --fix sdk/plugins

  if [[ -n "${CI}" ]]; then
    if [[ -z "$(git status --porcelain ./sdk/plugins)" ]];
    then
      exit 0
    else
      echo "Git is dirty"
      git status --porcelain ./sdk/plugins
      git --no-pager diff
      exit 1
    fi
  fi

popd
echo "✅ Generated plugin configurations are up to date."
