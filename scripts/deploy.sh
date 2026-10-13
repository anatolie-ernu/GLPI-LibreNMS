#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found. Run scripts/init-env.sh first."; exit 1; }

bash scripts/validate.sh

read_flag() {
  awk -F= -v key="$1" '$1 == key {print tolower($2)}' .env | tr -d '\r'
}

auto="$(read_flag AUTO_DISCOVERY_ENABLED)"
integration="$(read_flag INTEGRATION_ENABLED)"

profile_args=()
if [[ "$auto" == "true" || "$auto" == "1" || "$auto" == "yes" ]]; then
  profile_args+=(--profile auto-discovery)
fi
if [[ "$integration" == "true" || "$integration" == "1" || "$integration" == "yes" ]]; then
  profile_args+=(--profile integration)
fi

echo "Pulling images..."
docker compose -f docker-compose.yml "${profile_args[@]}" pull || true

if [[ "$auto" == "true" || "$auto" == "1" || "$auto" == "yes" ]]; then
  echo "Building NPM auto-discovery image..."
  docker compose -f docker-compose.yml --profile auto-discovery build npm-auto-discovery
fi

if [[ "$integration" == "true" || "$integration" == "1" || "$integration" == "yes" ]]; then
  echo "Building GLPI-LibreNMS integration API..."
  docker compose -f docker-compose.yml --profile integration build integration-api
fi

echo "Starting stack..."
docker compose -f docker-compose.yml "${profile_args[@]}" up -d --remove-orphans

echo
bash scripts/status.sh
