#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found. Run scripts/init-env.sh first."; exit 1; }

bash scripts/validate.sh

profile_args=()
auto="$(awk -F= '/^AUTO_DISCOVERY_ENABLED=/{print tolower($2)}' .env | tr -d '\r')"
if [[ "$auto" == "true" || "$auto" == "1" || "$auto" == "yes" ]]; then
  profile_args=(--profile auto-discovery)
fi

echo "Pulling images..."
docker compose -f docker-compose.yml "${profile_args[@]}" pull

echo "Starting stack..."
docker compose -f docker-compose.yml "${profile_args[@]}" up -d --remove-orphans

echo
bash scripts/status.sh
