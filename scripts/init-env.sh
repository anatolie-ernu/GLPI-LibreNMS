#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

force=false
domain=""
bind_ip=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=true; shift ;;
    --domain) domain="${2:?missing domain}"; shift 2 ;;
    --bind-ip) bind_ip="${2:?missing bind IP}"; shift 2 ;;
    *) echo "Usage: $0 [--force] [--domain DOMAIN] [--bind-ip IP]"; exit 2 ;;
  esac
done

if [[ -f .env && "$force" != true ]]; then
  echo "ERROR: .env already exists. Refusing to overwrite it."
  echo "Use --force only if you intentionally want a new configuration."
  exit 1
fi

cp .env.example .env

secret() {
  openssl rand -hex 24
}

sed -i "s|^GLPI_DB_PASSWORD=.*|GLPI_DB_PASSWORD=$(secret)|" .env
sed -i "s|^LIBRENMS_DB_PASSWORD=.*|LIBRENMS_DB_PASSWORD=$(secret)|" .env
sed -i "s|^PUID=.*|PUID=$(id -u)|" .env
sed -i "s|^PGID=.*|PGID=$(id -g)|" .env

if [[ -n "$domain" ]]; then
  sed -i "s|^DOMAIN_NAME=.*|DOMAIN_NAME=$domain|" .env
fi
if [[ -n "$bind_ip" ]]; then
  sed -i "s|^NPM_ADMIN_BIND_IP=.*|NPM_ADMIN_BIND_IP=$bind_ip|" .env
fi

chmod 600 .env
echo "Created .env with generated database passwords."
echo "Auto-discovery remains disabled until NPM API credentials are configured."
