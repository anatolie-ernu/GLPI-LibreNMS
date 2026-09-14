# Installation Guide

## 1. Requirements

Recommended baseline for a medium enterprise environment:

- Ubuntu Server 24.04 LTS
- 4-8 vCPU
- 16 GB RAM
- 200+ GB SSD
- Static management IP
- Internal DNS and NTP
- Reachability from the Docker host to managed network devices on UDP/161

For larger environments, RRD growth and database retention should be monitored and storage increased accordingly.

## 2. Clone repository

```bash
git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS
```

## 3. Prepare configuration

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

Replace at minimum:

```text
GLPI_DB_PASSWORD
LIBRENMS_DB_PASSWORD
PUID
PGID
```

Generate strong passwords with:

```bash
openssl rand -base64 32
```

Check the UID/GID that should own runtime data:

```bash
id
```

## 4. Install Docker

```bash
sudo ./scripts/install-docker.sh
```

Log out/in if Docker group membership was changed.

## 5. Validate configuration

```bash
./scripts/validate.sh
```

## 6. Deploy

```bash
./scripts/deploy.sh
```

Check:

```bash
./scripts/status.sh
```

## 7. Access applications

Default ports:

- GLPI: `http://SERVER-IP:8081`
- LibreNMS: `http://SERVER-IP:8000`

For production, expose these services only to the management network or publish them through a reverse proxy with HTTPS.

## 8. Initial network discovery order

Do not onboard the entire network immediately. Use this order:

1. One Cisco access switch.
2. Validate SNMPv3, interfaces, VLANs, FDB/MAC and LLDP/CDP.
3. One MikroTik switch/router.
4. Validate SNMPv3, interfaces, bridge/FDB data and neighbors.
5. Add core/distribution switches.
6. Add remaining access switches.
7. Deploy GLPI Agent to several test workstations.
8. Verify that the workstation IP/MAC can be correlated with LibreNMS FDB data.
9. Roll out GLPI Agent using GPO or another software deployment mechanism.

## 9. Firewall requirements

From LibreNMS host to network equipment:

```text
UDP/161  SNMP polling
ICMP     Recommended for availability checks
```

Optional later:

```text
UDP/162  SNMP traps to LibreNMS
UDP/514  Syslog to LibreNMS
```

These optional listeners are intentionally not enabled in the base compose file.

## 10. Upgrade

Always back up before upgrade:

```bash
./scripts/backup.sh
```

Then:

```bash
docker compose pull
docker compose up -d
```

GLPI is pinned by default. Change `GLPI_IMAGE` only after reviewing the target release notes. LibreNMS follows its official rolling Docker image model by default.
