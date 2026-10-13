#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found. Run: bash scripts/init-env.sh"; exit 1; }
[[ ! -f compose.yml ]] || { echo "ERROR: legacy compose.yml exists; only docker-compose.yml may be canonical."; exit 1; }

if grep -Eq 'CHANGE_ME_[A-Z0-9_]+' .env; then
  echo "ERROR: .env still contains CHANGE_ME placeholders."
  exit 1
fi

command -v docker >/dev/null 2>&1 || { echo "ERROR: docker is not installed"; exit 1; }
docker compose version >/dev/null

auto="$(awk -F= '/^AUTO_DISCOVERY_ENABLED=/{print tolower($2)}' .env | tr -d '\r')"
if [[ "$auto" == "true" || "$auto" == "1" || "$auto" == "yes" ]]; then
  npm_email="$(awk -F= '/^NPM_API_EMAIL=/{sub(/^[^=]*=/,""); print}' .env)"
  npm_pass="$(awk -F= '/^NPM_API_PASSWORD=/{sub(/^[^=]*=/,""); print}' .env)"
  [[ -n "$npm_email" && -n "$npm_pass" ]] || {
    echo "ERROR: AUTO_DISCOVERY_ENABLED=true requires NPM_API_EMAIL and NPM_API_PASSWORD."
    exit 1
  }
fi

echo "Validating canonical Docker Compose configuration..."
docker compose -f docker-compose.yml config -q
docker compose -f docker-compose.yml --profile auto-discovery config -q

echo "Checking that databases/cache are not host-published..."
if grep -Eq '^[[:space:]]*-[[:space:]]*["'\'' ]*(3306|6379):' docker-compose.yml; then
  echo "ERROR: database/cache host port detected in docker-compose.yml"
  exit 1
fi

echo "Checking known legacy hardcoded credentials..."
runtime_files=(docker-compose.yml install.sh configure.sh START.sh npm-auto-discovery.py scripts/init-env.sh scripts/deploy.sh scripts/status.sh scripts/backup.sh .env.example)
if grep -En 'root_secure_pass|glpi_secure_pass|librenms_secure_pass|Npm@ernu2025!' "${runtime_files[@]}"; then
  echo "ERROR: legacy hardcoded credential found in runtime/config files."
  exit 1
fi

echo "Validating shell syntax..."
for script in install.sh configure.sh START.sh scripts/*.sh; do
  bash -n "$script"
done

echo "Validating Python syntax and Service Desk policy..."
python3 -m py_compile npm-auto-discovery.py scripts/validate-servicedesk-policy.py
python3 scripts/validate-servicedesk-policy.py

echo "Validation passed."
