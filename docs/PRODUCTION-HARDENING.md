# Production Hardening and Canonical Docker Architecture

## Status

This document defines the canonical deployment architecture after Stage 1.5 hardening.

The only canonical Compose file is:

```text
docker-compose.yml
```

The legacy `compose.yml` and `init-databases.sql` were removed to prevent accidental deployment of a different architecture.

## Security decisions

### No hardcoded runtime credentials

Database passwords are generated into the untracked `.env` file by:

```bash
bash scripts/init-env.sh --domain example.internal
```

The repository contains placeholders only.

### Databases and Redis are internal-only

No host ports are published for:

- GLPI MySQL;
- LibreNMS MariaDB;
- LibreNMS Redis.

### Direct web application bindings

GLPI and LibreNMS direct ports bind to `DIRECT_BIND_IP`, which defaults to:

```text
127.0.0.1
```

They remain reachable through Nginx Proxy Manager on the shared proxy network.

### NPM admin interface

NPM Admin binds to `NPM_ADMIN_BIND_IP`, which defaults to loopback.

For remote administration use either:

- an SSH tunnel; or
- an explicit management-interface IP.

Do not expose port 81 to the Internet.

### Separate backend networks

```text
proxy-net
glpi-backend      internal=true
librenms-backend  internal=true
socket-net        internal=true
```

Only front-end application containers join `proxy-net`.

### Auto-discovery

Auto-discovery is disabled by default.

When enabled, it does not receive a direct Docker socket mount. It connects to a restricted Docker Socket Proxy that exposes only read operations needed for container discovery.

Enable only after NPM credentials have been changed/configured:

```env
AUTO_DISCOVERY_ENABLED=true
NPM_API_EMAIL=...
NPM_API_PASSWORD=...
```

Then:

```bash
bash scripts/deploy.sh
```

### NPM credentials

`NPM_API_EMAIL` and `NPM_API_PASSWORD` are credentials used by the auto-discovery client to authenticate to NPM.

They do not bootstrap or reset the NPM administrator.

Complete NPM's first-login flow first, then place the resulting account credentials in the private `.env` file if auto-discovery is required.

## Canonical service layout

```text
                         80 / 443
                            |
                            v
                   Nginx Proxy Manager
                            |
                    +-------+-------+
                    |               |
                    v               v
                  GLPI          LibreNMS
                    |               |
                    v          +----+----+
                 MySQL       MariaDB   Redis
                                  |
                                  v
                              Dispatcher
```

Optional:

```text
NPM auto-discovery
      |
      +--> NPM API
      |
      +--> docker-socket-proxy --> Docker Engine (read-only API subset)
```

## Deployment

```bash
sudo bash scripts/install-docker.sh

git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS

bash scripts/init-env.sh --domain example.internal
nano .env

bash scripts/validate.sh
bash scripts/deploy.sh
```

## Validation controls

`scripts/validate.sh` rejects:

- a reintroduced legacy `compose.yml`;
- unresolved `CHANGE_ME_...` secrets;
- missing auto-discovery API credentials when auto-discovery is enabled;
- database/cache host-port publication;
- known historical hardcoded credentials;
- invalid Compose;
- invalid shell/Python syntax;
- inconsistent Service Desk policy files.

## Production note

A green CI result means repository configuration is internally valid. It does not replace:

- staging deployment;
- application-level health checks;
- backup/restore testing;
- vulnerability review;
- firewall validation;
- HTTPS and DNS validation;
- GLPI/LibreNMS functional acceptance tests.
