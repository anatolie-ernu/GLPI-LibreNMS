# Backup and Restore

## Backup

Run:

```bash
bash scripts/backup.sh
```

The backup contains:

- GLPI database dump
- LibreNMS database dump
- GLPI persistent `/var/glpi` data
- LibreNMS persistent `/data` data
- compose file
- checksum manifest

The production `.env` file is intentionally not copied. Store secrets separately through your approved secret-management or encrypted backup process.

## Verify checksums

```bash
cd <BACKUP_DIRECTORY>
sha256sum -c SHA256SUMS
```

## Restore principles

Restore into a maintenance window and preferably into a clean test host first.

The correct order is:

1. Stop application services.
2. Restore persistent application data.
3. Restore databases.
4. Start services.
5. Validate GLPI and LibreNMS.
6. Run functional checks against a test endpoint and a test switch.

## Example restore workflow

Assume the backup path is stored in `BACKUP`:

```bash
BACKUP=/opt/backups/glpi-librenms/20260914_150000
```

Stop the application services while keeping database containers available when required:

```bash
docker compose stop glpi librenms librenms-dispatcher
```

Restore GLPI data:

```bash
gzip -dc "$BACKUP/glpi-data.tar.gz" | \
  docker compose run --rm -T glpi sh -lc 'rm -rf /var/glpi/* && tar -C /var/glpi -xzf -'
```

Restore LibreNMS data:

```bash
gzip -dc "$BACKUP/librenms-data.tar.gz" | \
  docker compose run --rm -T librenms sh -lc 'rm -rf /data/* && tar -C /data -xzf -'
```

Restore GLPI database:

```bash
gzip -dc "$BACKUP/glpi-db.sql.gz" | \
  docker compose exec -T glpi-db sh -lc \
  'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

Restore LibreNMS database:

```bash
gzip -dc "$BACKUP/librenms-db.sql.gz" | \
  docker compose exec -T librenms-db sh -lc \
  'mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

Start services:

```bash
docker compose up -d
bash scripts/status.sh
```

## Post-restore validation

GLPI:

- login works
- existing assets are visible
- recent inventory data is present
- agent inventory endpoint responds

LibreNMS:

- `lnms validate` passes or only expected warnings remain
- monitored devices are present
- polling/discovery resumes
- RRD graphs are present
- FDB/VLAN/interface data is visible

LibreNMS validation command:

```bash
docker compose exec librenms lnms validate
```

## Restore testing

A backup that has never been restored is not proven. Schedule periodic restore tests to an isolated Docker host and record RPO/RTO results.
