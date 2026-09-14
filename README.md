# GLPI + LibreNMS

Open-source IT asset inventory, network discovery and integrated IT Service Management stack based on **GLPI**, **LibreNMS**, and **Docker Compose**.

The project is designed for enterprise LAN environments with **Cisco** and **MikroTik** switches and focuses on correlating:

```text
Computer -> IP -> MAC -> VLAN -> Switch -> Physical Port
```

## Architecture decision

**GLPI is the integrated Service Desk / ITSM platform for this project.** A separate ticketing platform is not part of the baseline architecture.

```text
GLPI = CMDB + Asset Management + Service Desk / ITSM
LibreNMS = Network Monitoring + Discovery
Integration API = GLPI <-> LibreNMS correlation and automation
Active Directory / LDAP = identity source
```

See [ADR-001 — Use GLPI as the Integrated Service Desk](docs/ADR-001-GLPI-SERVICEDESK.md).

## Complete documentation

- **[Complete Romanian PDF Guide](docs/pdf/GLPI-LibreNMS-Complete-Guide-RO.pdf)** — installation, configuration, Cisco/MikroTik SNMPv3, GLPI Agent, GPO rollout, backup/restore, security, troubleshooting and operations.
- **[Complete Romanian Markdown Guide](docs/COMPLETE-GUIDE-RO.md)** — editable source used to generate the PDF.
- [Installation Guide](docs/INSTALL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Cisco SNMPv3](docs/CISCO-SNMPV3.md)
- [MikroTik SNMPv3](docs/MIKROTIK-SNMPV3.md)
- [GLPI Agent](docs/GLPI-AGENT.md)
- **[GLPI Service Desk Guide](docs/GLPI-SERVICEDESK.md)**
- **[Escalation, KPI and Reporting Model](docs/GLPI-ESCALATION-REPORTING.md)**
- **[Stage 2 — ITSM / Service Desk Integration](docs/STAGE-2-ITSM-SERVICEDESK.md)**
- [Integration API Design](integration-api/README.md)
- [Integration API OpenAPI Contract](integration-api/openapi.yaml)
- [Backup / Restore](docs/BACKUP-RESTORE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

The PDF is regenerated automatically by GitHub Actions when the documentation or deployment configuration changes.

## Components

- **GLPI** — IT Asset Management / CMDB, Service Desk / ITSM, tickets, incidents, requests, problems, changes, SLA/OLA, escalation, dashboards, users, hardware, software and GLPI Agent inventory.
- **LibreNMS** — network discovery, SNMP polling, interfaces, VLANs, FDB/MAC tables, ARP/NDP, LLDP/CDP neighbors and alerts.
- **GLPI Agent** — managed endpoint inventory.
- **Integration API** — asset/network correlation and LibreNMS alert-to-GLPI ticket automation.
- **Active Directory / LDAP** — users/groups and identity integration.
- **MySQL** — GLPI database.
- **MariaDB** — LibreNMS database.
- **Redis** — LibreNMS cache/session backend.
- **LibreNMS Dispatcher** — distributed/parallel polling service.

## Service Desk model

```text
L0  Self-Service / Knowledge Base
 |
 v
L1  Service Desk
 |
 +--> L2 Network
 +--> L2 Infrastructure
 +--> L2 Security
 +--> L2 Applications
 |
 v
L3  Senior Specialist / Head of IT / Vendor
```

Stage 2 includes:

- Incident and Request workflows;
- ticket-to-asset association;
- AD/LDAP users and groups;
- business calendars;
- SLA TTO/TTR;
- internal OLA;
- multi-level functional and hierarchical escalation;
- Major Incident workflow;
- ticket business rules and templates;
- Service Desk Manager and Head of IT dashboards;
- SLA/MTTA/MTTR/backlog/reopen/FCR reporting;
- LibreNMS alert -> GLPI incident automation;
- GLPI asset -> LibreNMS switch/port/VLAN enrichment.

## Supported network equipment in this repository

- Cisco IOS / IOS XE switches
- MikroTik RouterOS switches and routers
- Other SNMP-capable devices supported by LibreNMS

## Security defaults

- SNMPv3 `authPriv` is recommended for Cisco and MikroTik.
- SNMP access must be restricted to the LibreNMS management IP.
- Default/public SNMP communities must not be used in production.
- MikroTik SNMP write access is **not enabled by default**. It is only needed for the optional LibreNMS RouterOS VLAN helper script and carries additional risk.
- API and database secrets are kept out of Git.
- Integration API service accounts follow least privilege.
- GLPI/LibreNMS APIs should use HTTPS in production.

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
│   ├── GLPI-SERVICEDESK.md
│   ├── GLPI-ESCALATION-REPORTING.md
│   ├── STAGE-2-ITSM-SERVICEDESK.md
│   ├── ADR-001-GLPI-SERVICEDESK.md
│   ├── BACKUP-RESTORE.md
│   ├── TROUBLESHOOTING.md
│   └── pdf/
│       └── GLPI-LibreNMS-Complete-Guide-RO.pdf
├── integration-api/
│   ├── README.md
│   └── openapi.yaml
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

## Project status

**Stage 1:** Docker deployment + Cisco/MikroTik network discovery baseline.

**Stage 2:** Integrated GLPI Service Desk / ITSM, escalation/reporting and GLPI <-> LibreNMS automation — design and implementation in progress.

## License

MIT License. See `LICENSE`.
