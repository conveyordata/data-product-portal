#!/usr/bin/env bash

APP_VERSION=$(cat VERSION)
sed -i.bak "s/^version:.*/version: $APP_VERSION/" helm/Chart.yaml
sed -i.bak "s/^  tag:.*/  tag: "$APP_VERSION"/" helm/values.yaml
rm -f helm/*.bak
