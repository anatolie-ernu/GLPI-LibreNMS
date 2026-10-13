# GLPI-LibreNMS — Current Project Summary

## Current canonical architecture

```text
Nginx Proxy Manager
   |
   +--> GLPI --> dedicated MySQL
   |
   +--> LibreNMS --> dedicated MariaDB + Redis
                         |
                         +--> Dispatcher
```

Optional NPM auto-discovery uses a restricted Docker Socket Proxy.

Canonical file:

```text
docker-compose.yml
```

Legacy `compose.yml` has been removed.

## Security baseline

- no hardcoded runtime passwords;
- `.env` generated locally and ignored by Git;
- databases/cache not host-published;
- direct GLPI/LibreNMS ports loopback-only by default;
- NPM Admin loopback-only by default;
- auto-discovery disabled by default;
- no direct Docker socket mount in auto-discovery;
- CI rejects legacy credentials and inconsistent Service Desk policy.

## ITSM

GLPI is the integrated Service Desk and CMDB.

Stage 2 source of truth:

```text
config/glpi/
docs/GLPI-PRIORITY-SLA-ESCALATION-MATRIX.md
docs/GLPI-STAGE2-CONFIGURATION-RUNBOOK.md
```

## Current delivery status

**Repository:** hardened and suitable for pilot deployment after environment configuration.

**Production:** requires staging, backup/restore, HTTPS/DNS/firewall, GLPI/LibreNMS configuration, Service Desk acceptance testing, AD/LDAP pilot, device onboarding, and security sign-off.

See `README.md` and `docs/STAGE-2-IMPLEMENTATION-STATUS.md`.
