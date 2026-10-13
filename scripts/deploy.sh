#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found. Run scripts/init-env.sh first."; exit 1; }

bash scripts/validate.sh

auto="$(awk -F= '/^AUTO_DISCOVERY_ENABLED=/{print tolower($2)}' .env | tr -d '\r')"

echo "Pulling base images..."
docker compose -f docker-compose.yml pull

if [[ "$auto" == "true" || "$auto" == "1" || "$auto" == "yes" ]]; then
  echo "Building NPM auto-discovery image..."
  docker compose -f docker-compose.yml --profile auto-discovery build npm-auto-discovery
  echo "Starting base stack + auto-discovery profile..."
  docker compose -f docker-compose.yml --profile auto-discovery up -d --remove-orphans
else
  echo "Starting base stack..."
  docker compose -f docker-compose.yml up -d --remove-orphans
fi

echo
bash scripts/status.sh
