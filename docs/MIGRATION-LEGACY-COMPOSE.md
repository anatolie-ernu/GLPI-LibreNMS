# Migration from the Legacy Compose Stack

## Important

The repository previously contained two different Compose architectures:

```text
compose.yml
docker-compose.yml
```

They used different images, database layouts and persistent-volume paths.

Stage 1.5 establishes `docker-compose.yml` as the only canonical file.

## If the old stack was never deployed

No migration is required.

Initialize a fresh environment:

```bash
bash scripts/init-env.sh --domain example.internal
bash scripts/validate.sh
bash scripts/deploy.sh
```

## If the old stack contains real data

Do **not** simply run the new stack against old volumes.

Before migration:

1. stop changes/users;
2. identify which Compose file actually launched the running environment;
3. export GLPI database;
4. export LibreNMS database;
5. archive GLPI persistent data;
6. archive LibreNMS `/data`;
7. archive NPM `/data` and `/etc/letsencrypt` if NPM was used;
8. record image versions and container names;
9. verify backup checksums;
10. test restore on a separate host.

The hardened stack uses separate GLPI and LibreNMS databases. Migration from a legacy shared MySQL design therefore requires logical SQL dump/restore, not volume reuse.

## Recommended migration method

```text
Legacy DB/volumes
      |
      +--> logical SQL dumps
      +--> application data archives
      |
      v
Fresh hardened stack
      |
      +--> restore GLPI DB/data
      +--> restore LibreNMS DB/data
      +--> restore NPM data if compatible
      |
      v
Functional validation
```

## Required validation after migration

GLPI:

- login;
- assets;
- users/groups;
- ticket history;
- agent inventory;
- documents/attachments.

LibreNMS:

- device inventory;
- ports;
- FDB/MAC;
- VLANs;
- RRD graphs/history;
- alerts;
- dispatcher/polling.

NPM:

- proxy hosts;
- certificates;
- access lists;
- HTTPS routes.

Do not remove the legacy host/backup until functional and restore validation is complete.
