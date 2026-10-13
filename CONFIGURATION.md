# Configuration Guide — Canonical Stack

## Canonical files

```text
docker-compose.yml
.env.example
.env                # private, untracked
```

Never create a second Compose architecture.

## Initialize

```bash
bash scripts/init-env.sh --domain example.internal
nano .env
```

## Important variables

### General

```env
COMPOSE_PROJECT_NAME=glpi-librenms
TZ=Europe/Chisinau
PUID=1000
PGID=1000
DOMAIN_NAME=example.internal
```

### Bindings

```env
DIRECT_BIND_IP=127.0.0.1
NPM_PROXY_BIND_IP=0.0.0.0
NPM_ADMIN_BIND_IP=127.0.0.1
```

### Images

```env
GLPI_IMAGE=glpi/glpi:11
GLPI_DB_IMAGE=mysql:8.4
LIBRENMS_IMAGE=librenms/librenms:latest
LIBRENMS_DB_IMAGE=mariadb:11.4
REDIS_IMAGE=redis:7.2-alpine
NPM_IMAGE=jc21/nginx-proxy-manager:latest
```

Before Production, test and pin images/digests according to the organization's change process.

### Database secrets

Generated locally:

```env
GLPI_DB_PASSWORD=<private>
LIBRENMS_DB_PASSWORD=<private>
```

They must never appear in Git.

## Auto-discovery

Default:

```env
AUTO_DISCOVERY_ENABLED=false
```

After configuring NPM:

```env
AUTO_DISCOVERY_ENABLED=true
NPM_API_EMAIL=<private>
NPM_API_PASSWORD=<private>
```

Deploy again:

```bash
bash scripts/deploy.sh
```

## Service Desk policy

Version-controlled under:

```text
config/glpi/
```

Validate:

```bash
python3 scripts/validate-servicedesk-policy.py
```

## Validation

Always run:

```bash
bash scripts/validate.sh
```

before deployment or promotion.
