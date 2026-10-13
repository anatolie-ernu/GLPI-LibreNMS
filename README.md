# GLPI-LibreNMS — ERNU.EU

Self-hosted IT Asset Management, Service Desk / ITSM, network monitoring and endpoint-to-switch correlation platform.

**Canonical architecture:** GLPI + LibreNMS + Nginx Proxy Manager + Docker Compose  
**Network vendors:** Cisco IOS/IOS XE and MikroTik RouterOS  
**Service Desk:** GLPI native ITSM  
**Repository owner:** Anatolie Ernu / ERNU.EU

---

## What this project does

The target operational correlation is:

```text
User / Ticket
     |
     v
GLPI Service Desk
     |
     +--> Asset / CMDB / GLPI Agent
     |       |
     |       +--> Hostname / IP / MAC
     |
     +--> Integration API
             |
             v
          LibreNMS
             |
             +--> Switch
             +--> Port
             +--> VLAN
             +--> FDB/MAC
             +--> LLDP/CDP
             +--> Alert state
```

The Service Desk model is:

```text
L0  Self-Service / Knowledge Base
L1  SD-L1-ServiceDesk
L2  Network / Infrastructure / Security / Applications / Business Systems
L3  Senior / IT Management / Vendor Coordination
```

Priority is normalized to P1-P4 using Impact × Urgency.

---

## Canonical Docker deployment

There is exactly **one** supported Compose file:

```text
docker-compose.yml
```

The previous `compose.yml` architecture has been removed to prevent accidental deployment of a different stack.

Canonical services:

- Nginx Proxy Manager
- official GLPI image
- dedicated GLPI MySQL
- LibreNMS
- dedicated LibreNMS MariaDB
- LibreNMS Redis
- LibreNMS Dispatcher
- optional NPM auto-discovery
- optional restricted Docker Socket Proxy

Security defaults:

- no database/cache host ports;
- GLPI/LibreNMS direct ports bind to loopback by default;
- NPM admin binds to loopback by default;
- database passwords are generated into the untracked `.env`;
- auto-discovery is disabled until explicitly configured;
- auto-discovery does not mount the Docker socket directly.

See [Production Hardening](docs/PRODUCTION-HARDENING.md).

---

## Quick start

### 1. Install Docker

```bash
sudo bash scripts/install-docker.sh
```

### 2. Initialize private configuration

```bash
bash scripts/init-env.sh --domain example.internal
nano .env
```

For a management-interface NPM admin binding:

```bash
bash scripts/init-env.sh \
  --domain example.internal \
  --bind-ip 10.0.0.50
```

### 3. Validate

```bash
bash scripts/validate.sh
```

### 4. Deploy

```bash
bash scripts/deploy.sh
```

### 5. Check status

```bash
bash scripts/status.sh
```

Direct diagnostic ports default to:

```text
127.0.0.1:8081 -> GLPI
127.0.0.1:8000 -> LibreNMS
127.0.0.1:81   -> NPM Admin
```

NPM publishes HTTP/HTTPS on ports 80/443.

---

## NPM auto-discovery

Auto-discovery is intentionally disabled by default.

After NPM first-login setup and credential change:

```env
AUTO_DISCOVERY_ENABLED=true
NPM_API_EMAIL=<private value>
NPM_API_PASSWORD=<private value>
```

Then:

```bash
bash scripts/deploy.sh
```

The discovery container talks to Docker through a restricted socket-proxy profile rather than mounting `/var/run/docker.sock` directly.

---

## GLPI Service Desk / ITSM

The project standardizes on GLPI Service Desk instead of adding a separate ticketing platform.

Key documents:

- [Stage 2 Implementation Status](docs/STAGE-2-IMPLEMENTATION-STATUS.md)
- [GLPI Service Desk Guide](docs/GLPI-SERVICEDESK.md)
- [Priority / SLA / OLA / Escalation Policy](docs/GLPI-PRIORITY-SLA-ESCALATION-MATRIX.md)
- [Stage 2 Configuration Runbook](docs/GLPI-STAGE2-CONFIGURATION-RUNBOOK.md)
- [Escalation and Reporting](docs/GLPI-ESCALATION-REPORTING.md)
- [Stage 2 ITSM Plan](docs/STAGE-2-ITSM-SERVICEDESK.md)

Machine-readable source of truth:

- [config/glpi/servicedesk-policy.yaml](config/glpi/servicedesk-policy.yaml)
- [config/glpi/priority-matrix.csv](config/glpi/priority-matrix.csv)
- [config/glpi/sla-policies.csv](config/glpi/sla-policies.csv)
- [config/glpi/support-groups.csv](config/glpi/support-groups.csv)
- [config/glpi/escalation-rules.csv](config/glpi/escalation-rules.csv)

Baseline SLA:

| Priority | TTO | TTR |
|---|---:|---:|
| P1 Critical | 15 min | 2 h |
| P2 High | 30 min | 4 h |
| P3 Medium | 4 h | 1 business day |
| P4 Low | 1 business day | 3 business days |

---

## Network integration

Cisco:

- [Cisco SNMPv3](docs/CISCO-SNMPV3.md)
- [Cisco example](config/cisco/snmpv3-example.txt)

MikroTik:

- [MikroTik SNMPv3](docs/MIKROTIK-SNMPV3.md)
- [MikroTik example](config/mikrotik/snmpv3-example.rsc)

Production baseline is SNMPv3 `authPriv`, read-only, restricted to the LibreNMS management source.

---

## Endpoint inventory

GLPI Agent provides endpoint inventory.

See:

- [GLPI Agent Deployment](docs/GLPI-AGENT.md)

Target correlation:

```text
GLPI asset
  Hostname / Serial / User / IP / MAC
                |
                v
LibreNMS FDB/ARP/topology
                |
                v
Switch / Port / VLAN
```

---

## Integration API

The API contract is present, but the executable service is **not yet implemented**.

Current files:

- `integration-api/README.md`
- `integration-api/openapi.yaml`

Planned responsibilities:

- IP/MAC -> switch/port/VLAN enrichment;
- LibreNMS alert -> GLPI incident;
- deduplication;
- recovery correlation;
- audit logging.

---

## Backup and restore

```bash
bash scripts/backup.sh
```

See [Backup / Restore](docs/BACKUP-RESTORE.md).

A backup is not considered proven until a restore test has been completed on an isolated host.

---

## Complete documentation

- [Complete Romanian Guide — Markdown](docs/COMPLETE-GUIDE-RO.md)
- [Generated Complete Romanian PDF](docs/pdf/GLPI-LibreNMS-Complete-Guide-RO.pdf)
- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALL.md)
- [Production Hardening](docs/PRODUCTION-HARDENING.md)
- [Legacy Compose Migration](docs/MIGRATION-LEGACY-COMPOSE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

The repository also contains ERNU.EU-branded DOCX/PDF deliverables.

---

## Current status

### Implemented in repository

- canonical hardened Docker stack;
- NPM reverse proxy;
- GLPI;
- LibreNMS + Dispatcher;
- separate databases;
- Redis;
- optional hardened NPM auto-discovery;
- installation/validation/backup scripts;
- Cisco/MikroTik SNMPv3 guidance;
- Service Desk policy source-of-truth;
- CI validation;
- PDF documentation generation.

### Specified but still requiring deployment/configuration

- AD/LDAP pilot;
- GLPI groups/profiles/categories;
- production SLA/OLA configuration;
- escalation levels and notifications;
- dashboards;
- GLPI Agent rollout;
- Cisco/MikroTik onboarding.

### Planned implementation

- executable Integration API;
- automated LibreNMS alert -> GLPI ticket creation;
- deduplication/recovery state;
- end-to-end integration tests.

---

## Production gate

The repository is **pilot-ready after environment configuration**, not automatically production-approved.

Before Production:

1. stage the stack;
2. configure DNS/HTTPS;
3. validate firewall exposure;
4. configure GLPI/LibreNMS;
5. apply Service Desk policy;
6. configure AD/LDAP pilot;
7. onboard pilot network devices;
8. deploy GLPI Agent to pilot endpoints;
9. test backup/restore;
10. run accelerated SLA/escalation tests;
11. review image versions/digests;
12. complete security and acceptance sign-off.

---

## License / branding

ERNU.EU documentation and repository licensing terms apply as stated in the repository.

**Author:** Anatolie Ernu  
**Brand:** ERNU.EU
