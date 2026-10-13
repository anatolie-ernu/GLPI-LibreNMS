# Installation Guide — Canonical Hardened Stack

## 1. Host baseline

Recommended starting point:

- Ubuntu Server 24.04 LTS;
- 4-8 vCPU;
- 16 GB RAM;
- 200+ GB SSD;
- static management IP;
- internal DNS;
- NTP;
- routed reachability to Cisco/MikroTik management addresses.

## 2. Clone

```bash
cd /opt
git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS
```

## 3. Install Docker

```bash
sudo bash scripts/install-docker.sh
```

Log out/in if Docker group membership changed.

Verify:

```bash
docker --version
docker compose version
```

## 4. Initialize .env

```bash
bash scripts/init-env.sh --domain example.internal
```

Optional NPM admin management bind:

```bash
bash scripts/init-env.sh \
  --domain example.internal \
  --bind-ip 10.0.0.50
```

Review:

```bash
nano .env
chmod 600 .env
```

The initializer generates GLPI and LibreNMS database passwords.

Do not commit `.env`.

## 5. Validate

```bash
bash scripts/validate.sh
```

The validator checks:

- one canonical Compose file;
- unresolved secret placeholders;
- Compose syntax;
- no MySQL/Redis host publication;
- absence of historical hardcoded credentials in runtime files;
- Bash/Python syntax;
- GLPI Service Desk policy consistency.

## 6. Deploy

```bash
bash scripts/deploy.sh
```

Status:

```bash
bash scripts/status.sh
```

## 7. Initial access

Default secure bindings:

```text
127.0.0.1:81    NPM Admin
127.0.0.1:8081  GLPI direct diagnostic access
127.0.0.1:8000  LibreNMS direct diagnostic access
0.0.0.0:80      NPM HTTP proxy
0.0.0.0:443     NPM HTTPS proxy
```

For remote NPM administration use SSH tunneling or set `NPM_ADMIN_BIND_IP` to the management-interface IP.

Do not expose port 81 publicly.

## 8. Configure NPM

Complete the vendor first-login flow and change credentials.

Then either create proxy hosts manually:

```text
glpi.<DOMAIN>      -> glpi:80
librenms.<DOMAIN>  -> librenms:8000
```

or enable auto-discovery after putting NPM API credentials in the private `.env`:

```env
AUTO_DISCOVERY_ENABLED=true
NPM_API_EMAIL=...
NPM_API_PASSWORD=...
```

Then:

```bash
bash scripts/deploy.sh
```

## 9. HTTPS / DNS

Create internal DNS records for GLPI and LibreNMS.

Configure NPM certificates appropriate for the environment.

Do not assume public Let's Encrypt issuance will work for private/internal-only names; use the organization's certificate model where required.

## 10. LibreNMS pilot

Add one Cisco switch using SNMPv3 authPriv.

Validate:

- ports;
- VLANs;
- FDB/MAC;
- LLDP/CDP;
- sensors;
- polling.

Then add one MikroTik and validate bridge/FDB/neighbors.

## 11. GLPI pilot

Configure GLPI, then follow:

- `docs/GLPI-STAGE2-CONFIGURATION-RUNBOOK.md`
- `docs/GLPI-AGENT.md`

Pilot 2-5 endpoints before domain-wide rollout.

## 12. Backup

```bash
bash scripts/backup.sh
```

Test restore separately before Production.

## 13. Migration warning

If any older Compose architecture contains real data, read:

```text
docs/MIGRATION-LEGACY-COMPOSE.md
```

Do not reuse old database volumes blindly.
