#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a
  source .env
  set +a
fi

echo "=== Docker Compose services ==="
docker compose ps

echo
if command -v curl >/dev/null 2>&1; then
  echo "=== HTTP checks ==="
  curl -fsS -o /dev/null -w "GLPI      HTTP %{http_code}\n" "http://127.0.0.1:${GLPI_HTTP_PORT:-8081}/" || echo "GLPI      unavailable"
  curl -fsS -o /dev/null -w "LibreNMS  HTTP %{http_code}\n" "http://127.0.0.1:${LIBRENMS_HTTP_PORT:-8000}/" || echo "LibreNMS  unavailable"
fi
