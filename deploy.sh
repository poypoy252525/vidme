#!/bin/bash
# Full rebuild and restart script
# Usage: ./deploy.sh

set -e

echo "Stopping any running containers..."
docker compose down

echo "Rebuilding all services without cache..."
docker compose build --no-cache

echo "Starting containers..."
docker compose up -d

echo "✓ Deployment complete"
docker compose ps
