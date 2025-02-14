#!/bin/bash

# Start the FastAPI app in the background
poetry run python -m app.local_startup &
PID=$!  # Store the process ID

# Wait for the server to be ready
echo "Waiting for server to start..."
until curl -s http://localhost:5050/openapi.json > /dev/null; do
  sleep 1
done

# Fetch OpenAPI JSON
echo "Server started! Fetching OpenAPI JSON..."
curl -s http://localhost:5050/openapi.json -o openapi.json

# Stop the server
echo "Stopping server..."
kill $PID
