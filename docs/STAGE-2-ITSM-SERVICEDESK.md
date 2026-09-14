# Stage 2 — ITSM / Service Desk Integration

## Objective

Extend the GLPI + LibreNMS platform from asset/network inventory into a practical IT Service Management platform while preserving clear ownership of data:

- **GLPI** — ITSM, Service Desk, CMDB, assets, users, SLA/OLA, incidents, requests, problems, changes and knowledge base.
- **LibreNMS** — network monitoring, device state, ports, VLAN, FDB/MAC, alerts and topology evidence.
- **GLPI Agent** — endpoint inventory.
- **Active Directory / LDAP** — users, groups and identity source.
- **Integration API** — controlled correlation layer between GLPI and LibreNMS.

Target workflow:

```text
User / Monitoring Alert
        |
        v
      GLPI Ticket
        |
        +--> Requester / Department / SLA
        +--> Affected Asset
        |       |
        |       +--> Hostname / IP / MAC
        |                    |
        |                    v
        |              Integration API
        |                    |
        |                    v
        |                 LibreNMS
        |                    |
        |        Switch / Port / VLAN / Status
        |
        +--> Assignment Group / Technician
        +--> Tasks / Followups / Solution
        +--> Knowledge Base
```

## Scope

### Stage 2.1 — GLPI Service Desk baseline

- Enable and configure the GLPI Assistance module.
- Define Incident and Request workflows.
- Define support groups and technician profiles.
- Define ticket categories.
- Define ticket templates.
- Associate tickets with affected assets.
- Configure email ticket creation only after base workflows are validated.
- Configure knowledge base categories.

### Stage 2.2 — Identity and organizational model

- Connect GLPI to Active Directory / LDAP.
- Import users and support groups.
- Map entities, departments and locations.
- Define requester, observer, technician and approver roles.
- Test authentication and authorization with pilot accounts before broad rollout.

### Stage 2.3 — SLA / OLA

Define operational targets using GLPI Service Levels:

| Priority | Example TTO | Example TTR | Typical use |
|---|---:|---:|---|
| Critical | 15 min | 2 h | Core service outage / major network failure |
| High | 30 min | 4 h | Significant user/service impact |
| Medium | 4 h | 1 business day | Standard incidents |
| Low | 1 business day | 3 business days | Non-urgent requests |

These values are examples only. Production values must be approved against organizational support hours and contracts.

Configure:

- working calendars;
- SLA TTO (Time To Own);
- SLA TTR (Time To Resolve);
- OLA between internal groups where needed;
- escalation rules;
- SLA reminder notifications;
- automatic actions/cron validation.

### Stage 2.4 — Ticket automation

Create business rules for tickets, for example:

```text
Category: Network / Connectivity
  -> Group: Network Team
  -> Priority: Medium
  -> SLA: Network Standard

Category: Infrastructure / Server
  -> Group: Infrastructure Team

Category: Security / Endpoint
  -> Group: Security Team
  -> Priority: High
```

Use ticket templates to make fields mandatory and to predefine category, group, urgency and SLA where appropriate.

### Stage 2.5 — Asset-aware Service Desk

Every incident that affects an endpoint or managed infrastructure device should be associated with an asset whenever possible.

Target ticket context:

```text
Ticket: INC-2026-00421
Requester: User Name
Category: Network / Connectivity
Affected asset: HQ-PC-043

GLPI asset data:
  Serial: ABC123456
  Model: Dell Latitude
  OS: Windows 11
  IP: 10.129.21.43
  MAC: 00:25:90:AB:CD:EF

LibreNMS enrichment:
  Switch: HQ-ACCESS-SW-04
  Port: Gi1/0/31
  VLAN: 129
  Port state: up/down
  Last FDB seen: timestamp
```

## LibreNMS -> GLPI integration

### Primary use case: alert to ticket

```text
LibreNMS Alert
      |
      | HTTP/API transport
      v
Integration API
      |
      | normalize / deduplicate / enrich
      v
GLPI Ticket API
```

Examples:

- device down;
- uplink down;
- excessive interface errors;
- power supply failure;
- temperature threshold;
- high utilization;
- monitored service failure.

### Required controls

The integration must not create duplicate tickets for every polling cycle.

Use an idempotency/correlation key such as:

```text
librenms:<device_id>:<rule_id>:<fault_object>
```

Store the relationship:

```text
LibreNMS alert ID -> GLPI ticket ID
```

When the alert recovers, the integration should add a follow-up or recovery event to the existing GLPI ticket. Automatic ticket closure should be optional and policy-controlled.

## GLPI -> LibreNMS enrichment

When a ticket has an affected asset with IP/MAC information, the integration service should be able to request current network evidence.

Target API operations:

```text
GET /v1/endpoints/by-ip/{ip}
GET /v1/endpoints/by-mac/{mac}
GET /v1/assets/{asset_id}/network
GET /v1/librenms/alerts/{alert_id}
POST /v1/events/librenms
```

Expected result:

```json
{
  "hostname": "HQ-PC-043",
  "ip": "10.129.21.43",
  "mac": "00:25:90:AB:CD:EF",
  "switch": "HQ-ACCESS-SW-04",
  "port": "Gi1/0/31",
  "vlan": 129,
  "port_status": "up",
  "evidence": {
    "source": "librenms",
    "last_seen": "2026-09-14T15:42:00+03:00"
  }
}
```

## Security model

- GLPI and LibreNMS API tokens are stored only as secrets, never committed to Git.
- Integration API gets least-privilege service accounts.
- LibreNMS token should be read-only where possible.
- GLPI integration account should only have permissions required to read assets and create/update Service Desk records.
- Integration API must be available only on the management network or behind an authenticated reverse proxy.
- All API communication should use HTTPS in production.
- Every automatic ticket/event action must be logged.
- Do not expose database services or Redis outside Docker networks.

## Acceptance criteria

Stage 2 is considered operational when all of the following are demonstrated:

- [ ] AD/LDAP user login works for pilot users.
- [ ] Support groups and technician roles are defined.
- [ ] Incident and Request categories are configured.
- [ ] SLA TTO/TTR works against a configured business calendar.
- [ ] Business rules assign tickets to the correct support group.
- [ ] A ticket can be associated with a GLPI computer or network device.
- [ ] The same asset's MAC can be resolved to a LibreNMS switch/port where network data allows it.
- [ ] One LibreNMS test alert creates exactly one GLPI incident.
- [ ] Repeated alert notifications do not create duplicate incidents.
- [ ] Recovery adds an event/follow-up to the same incident.
- [ ] API secrets are absent from the repository and logs.
- [ ] Backup and restore cover Service Desk data.

## Out of scope for the first Stage 2 implementation

- full CMDB reconciliation engine;
- automatic remediation;
- automatic shutdown/no-shutdown of network ports;
- SNMP write-based corrective actions;
- automatic closure of all recovered incidents;
- public Internet exposure of the Service Desk without reverse proxy/SSO/hardening.

## Delivery order

1. Configure GLPI Service Desk manually and validate workflow.
2. Configure AD/LDAP pilot authentication.
3. Configure categories, groups, calendars, SLA/OLA and rules.
4. Validate ticket-to-asset relationship.
5. Create Integration API service scaffold.
6. Implement LibreNMS read-only enrichment.
7. Implement LibreNMS alert webhook ingestion.
8. Implement GLPI ticket creation/update.
9. Add deduplication and recovery handling.
10. Add end-to-end tests and production hardening.
