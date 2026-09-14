# GLPI + LibreNMS

Open-source IT asset inventory and network discovery stack based on **GLPI**, **LibreNMS**, and **Docker Compose**.

The project is designed for enterprise LAN environments with **Cisco** and **MikroTik** switches and focuses on correlating:

```text
Computer -> IP -> MAC -> VLAN -> Switch -> Physical Port
```

## Complete documentation

- **[Complete Romanian PDF Guide](docs/pdf/GLPI-LibreNMS-Complete-Guide-RO.pdf)** — installation, configuration, Cisco/MikroTik SNMPv3, GLPI Agent, GPO rollout, backup/restore, security, troubleshooting and operations.
- **[Complete Romanian Markdown Guide](docs/COMPLETE-GUIDE-RO.md)** — editable source used to generate the PDF.
- [Installation Guide](docs/INSTALL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Cisco SNMPv3](docs/CISCO-SNMPV3.md)
- [MikroTik SNMPv3](docs/MIKROTIK-SNMPV3.md)
- [GLPI Agent](docs/GLPI-AGENT.md)
- [Backup / Restore](docs/BACKUP-RESTORE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

The PDF is regenerated automatically by GitHub Actions when the documentation or deployment configuration changes.

## Components

- **GLPI** — IT Asset Management / CMDB, computers, users, hardware, software and GLPI Agent inventory.
- **LibreNMS** — network discovery, SNMP polling, interfaces, VLANs, FDB/MAC tables, ARP/NDP and LLDP/CDP neighbors.
- **MySQL** — GLPI database.
- **MariaDB** — LibreNMS database.
- **Redis** — LibreNMS cache/session backend.
- **LibreNMS Dispatcher** — distributed/parallel polling service.

## Supported network equipment in this repository

- Cisco IOS / IOS XE switches
- MikroTik RouterOS switches and routers
- Other SNMP-capable devices supported by LibreNMS

## Security defaults

- SNMPv3 `authPriv` is recommended for Cisco and MikroTik.
- SNMP access must be restricted to the LibreNMS management IP.
- Default/public SNMP communities must not be used in production.
- MikroTik SNMP write access is **not enabled by default**. It is only needed for the optional LibreNMS RouterOS VLAN helper script and carries additional risk.
- Secrets are kept in `.env`, which is excluded from Git.

## Repository structure

```text
.
├── compose.yml
├── .env.example
├── .gitignore
├── SECURITY.md
├── docs/
│   ├── COMPLETE-GUIDE-RO.md
│   ├── INSTALL.md
│   ├── ARCHITECTURE.md
│   ├── CISCO-SNMPV3.md
│   ├── MIKROTIK-SNMPV3.md
│   ├── GLPI-AGENT.md
│   ├── BACKUP-RESTORE.md
│   ├── TROUBLESHOOTING.md
│   └── pdf/
│       └── GLPI-LibreNMS-Complete-Guide-RO.pdf
├── config/
│   ├── cisco/
│   │   └── snmpv3-example.txt
│   └── mikrotik/
│       └── snmpv3-example.rsc
├── scripts/
│   ├── install-docker.sh
│   ├── deploy.sh
│   ├── status.sh
│   ├── validate.sh
│   └── backup.sh
└── .github/workflows/
    ├── validate.yml
    └── build-docs-pdf.yml
```

## Quick start

```bash
git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS
cp .env.example .env
nano .env
chmod 600 .env
sudo bash scripts/install-docker.sh
bash scripts/validate.sh
bash scripts/deploy.sh
```

Default local ports:

- GLPI: `http://SERVER-IP:8081`
- LibreNMS: `http://SERVER-IP:8000`

For production, place both applications behind a reverse proxy with HTTPS and restrict direct access to the management network.

## Recommended deployment flow

1. Deploy Docker stack.
2. Add one Cisco switch through SNMPv3.
3. Verify interfaces, FDB/MAC, VLAN and LLDP/CDP discovery.
4. Add one MikroTik device through SNMPv3.
5. Verify bridge ports, interfaces, MAC/FDB and neighbors.
6. Deploy GLPI Agent to several test workstations.
7. Validate IP/MAC correlation between GLPI and LibreNMS.
8. Roll out GLPI Agent through GPO or endpoint management.
9. Add remaining network devices.
10. Configure backup, HTTPS, monitoring and access controls.

## Project status

**Stage 1:** Docker deployment + Cisco/MikroTik network discovery baseline.

Planned next stage: endpoint rollout with GLPI Agent and automated IP/MAC/switch/port correlation.

## License

MIT License. See `LICENSE`.
