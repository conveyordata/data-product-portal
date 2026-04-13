#!/usr/bin/env bash
set -e

# Check if the generated API is up to date
cd frontend

echo "Checking if generated API is up to date..."

# Run generate-api
npm run generate-api

# Check if there are any changes in the generated files
if ! git diff --exit-code src/store/api/services/generated/; then
    echo "❌ ERROR: Generated API files are out of date!"
    echo "Please run 'npm run generate-api' in the frontend directory and commit the changes."
    exit 1
fi

echo "✅ Generated API files are up to date."
