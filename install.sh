#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

domain=""
bind_ip="127.0.0.1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) domain="${2:?missing domain}"; shift 2 ;;
    --bind-ip) bind_ip="${2:?missing bind IP}"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--domain example.internal] [--bind-ip 127.0.0.1]"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || {
  echo "ERROR: Docker is not installed. Run: sudo bash scripts/install-docker.sh"
  exit 1
}
docker compose version >/dev/null 2>&1 || {
  echo "ERROR: Docker Compose plugin is not installed."
  exit 1
}

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: current user cannot access Docker."
  echo "Log in again after adding the user to the docker group, or run with appropriate privileges."
  exit 1
fi

if [[ -z "$domain" && -t 0 ]]; then
  read -r -p "Internal DNS domain [example.internal]: " domain
fi
domain="${domain:-example.internal}"

if [[ "$bind_ip" == "127.0.0.1" && -t 0 ]]; then
  read -r -p "NPM admin bind IP [127.0.0.1]: " answer
  bind_ip="${answer:-127.0.0.1}"
fi

if [[ ! -f .env ]]; then
  bash scripts/init-env.sh --domain "$domain" --bind-ip "$bind_ip"
else
  echo "Using existing .env; it will not be overwritten."
fi

bash scripts/validate.sh

echo "Pulling canonical images..."
docker compose -f docker-compose.yml pull

echo "Starting base stack..."
docker compose -f docker-compose.yml up -d

echo
bash scripts/status.sh

cat <<'EOF'

Base deployment started.

Security defaults:
- MySQL/MariaDB/Redis are NOT published on host ports.
- GLPI and LibreNMS direct ports bind to DIRECT_BIND_IP (127.0.0.1 by default).
- NPM admin binds to NPM_ADMIN_BIND_IP (127.0.0.1 by default).
- NPM proxy ports 80/443 are published.
- NPM auto-discovery is disabled by default.

Next:
1. Access NPM admin locally or through an SSH tunnel.
2. Complete NPM first-login setup and change its credentials.
3. Create proxy hosts manually for:
     glpi:80
     librenms:8000
   OR configure NPM_API_EMAIL/NPM_API_PASSWORD in .env,
   set AUTO_DISCOVERY_ENABLED=true, then run:
     bash scripts/deploy.sh
4. Configure HTTPS and internal DNS.
EOF
