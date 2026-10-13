#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

cat <<'EOF'
GLPI-LibreNMS — canonical production-hardened entry point

1) Install Docker (if needed):
   sudo bash scripts/install-docker.sh

2) Initialize configuration:
   bash scripts/init-env.sh --domain example.internal --bind-ip 127.0.0.1

3) Review configuration:
   nano .env

4) Validate:
   bash scripts/validate.sh

5) Deploy:
   bash scripts/deploy.sh

6) Status:
   bash scripts/status.sh

7) Backup:
   bash scripts/backup.sh

Canonical compose file:
   docker-compose.yml

See:
   README.md
   docs/PRODUCTION-HARDENING.md
   docs/MIGRATION-LEGACY-COMPOSE.md
EOF
