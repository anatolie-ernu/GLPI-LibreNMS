#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 DOMAIN [NPM_ADMIN_BIND_IP]"
  echo "Example: $0 arcom.md 10.128.20.50"
  exit 2
fi

domain="$1"
bind_ip="${2:-127.0.0.1}"

if [[ ! -f .env ]]; then
  bash scripts/init-env.sh --domain "$domain" --bind-ip "$bind_ip"
else
  sed -i "s|^DOMAIN_NAME=.*|DOMAIN_NAME=$domain|" .env
  sed -i "s|^NPM_ADMIN_BIND_IP=.*|NPM_ADMIN_BIND_IP=$bind_ip|" .env
  chmod 600 .env
fi

echo "Configuration updated."
echo "Review .env, then run: bash scripts/deploy.sh"
