#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found."; exit 1; }

set -a
# shellcheck disable=SC1091
source .env
set +a

profile_args=()
case "${AUTO_DISCOVERY_ENABLED:-false}" in
  true|TRUE|1|yes|YES) profile_args=(--profile auto-discovery) ;;
esac

echo "=== Docker Compose services ==="
docker compose -f docker-compose.yml "${profile_args[@]}" ps

echo
if command -v curl >/dev/null 2>&1; then
  echo "=== Direct HTTP checks ==="
  curl -fsS -o /dev/null -w "GLPI      HTTP %{http_code}\n" "http://${DIRECT_BIND_IP:-127.0.0.1}:${GLPI_HTTP_PORT:-8081}/" || echo "GLPI      unavailable"
  curl -fsS -o /dev/null -w "LibreNMS  HTTP %{http_code}\n" "http://${DIRECT_BIND_IP:-127.0.0.1}:${LIBRENMS_HTTP_PORT:-8000}/" || echo "LibreNMS  unavailable"
  curl -fsS -o /dev/null -w "NPM Admin HTTP %{http_code}\n" "http://${NPM_ADMIN_BIND_IP:-127.0.0.1}:${NPM_ADMIN_PORT:-81}/" || echo "NPM Admin unavailable"
fi
