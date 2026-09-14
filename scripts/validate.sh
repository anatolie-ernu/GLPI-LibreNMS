#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Run: cp .env.example .env"
  exit 1
fi

if grep -q 'CHANGE_ME' .env; then
  echo "ERROR: .env still contains CHANGE_ME placeholders."
  exit 1
fi

command -v docker >/dev/null 2>&1 || { echo "ERROR: docker is not installed"; exit 1; }
docker compose version >/dev/null

echo "Validating Docker Compose configuration..."
docker compose config -q

echo "Validating shell scripts..."
for script in scripts/*.sh; do
  bash -n "$script"
done

echo "Validation passed."
