#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found. Copy .env.example to .env first."; exit 1; }

./scripts/validate.sh

echo "Pulling images..."
docker compose pull

echo "Starting stack..."
docker compose up -d

echo
./scripts/status.sh
