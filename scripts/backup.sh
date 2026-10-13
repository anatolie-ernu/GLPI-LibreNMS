#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "ERROR: .env not found."; exit 1; }
set -a
# shellcheck disable=SC1091
source .env
set +a

STAMP="$(date +%Y%m%d_%H%M%S)"
DEST="${BACKUP_DIR:-./backups}/${STAMP}"
mkdir -p "$DEST"
chmod 700 "$DEST"

echo "Backing up GLPI database..."
docker compose -f docker-compose.yml exec -T glpi-db sh -lc   'mysqldump --single-transaction --routines --triggers -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'   | gzip -c >"$DEST/glpi-db.sql.gz"

echo "Backing up LibreNMS database..."
docker compose -f docker-compose.yml exec -T librenms-db sh -lc   'mariadb-dump --single-transaction --routines --triggers -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'   | gzip -c >"$DEST/librenms-db.sql.gz"

echo "Backing up GLPI persistent data..."
docker compose -f docker-compose.yml exec -T glpi sh -lc 'tar -C /var/glpi -czf - .' >"$DEST/glpi-data.tar.gz"

echo "Backing up LibreNMS persistent data..."
docker compose -f docker-compose.yml exec -T librenms sh -lc 'tar -C /data -czf - .' >"$DEST/librenms-data.tar.gz"

echo "Backing up NPM data..."
docker compose -f docker-compose.yml exec -T nginx-proxy-manager sh -lc 'tar -C /data -czf - .' >"$DEST/npm-data.tar.gz"
docker compose -f docker-compose.yml exec -T nginx-proxy-manager sh -lc 'tar -C /etc/letsencrypt -czf - .' >"$DEST/npm-letsencrypt.tar.gz"

case "${INTEGRATION_ENABLED:-false}" in
  true|TRUE|1|yes|YES)
    echo "Backing up Integration API correlation state..."
    docker compose -f docker-compose.yml --profile integration exec -T integration-api \
      sh -lc 'tar -C /data -czf - .' >"$DEST/integration-correlations.tar.gz"
    ;;
esac

cp .env.example "$DEST/env-template.txt"
cp docker-compose.yml "$DEST/docker-compose.yml"

sha256sum "$DEST"/* >"$DEST/SHA256SUMS"

cat >"$DEST/README.txt" <<EOF
Backup created: $(date --iso-8601=seconds)
Repository: anatolie-ernu/GLPI-LibreNMS
Contains GLPI/LibreNMS database dumps, application data, and NPM data/certificates.
The production .env file is intentionally NOT copied.
Store secrets using the approved secret-management/backup process.
EOF

chmod 600 "$DEST"/*
echo "Backup completed: $DEST"
