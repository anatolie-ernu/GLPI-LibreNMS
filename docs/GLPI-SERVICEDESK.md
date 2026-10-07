# GLPI Service Desk Configuration Guide

This guide defines the recommended Service Desk baseline for the GLPI + LibreNMS project.

## 1. Operating model

Use GLPI as the authoritative platform for:

- incidents;
- service requests;
- problems;
- changes;
- ticket assignment;
- SLA/OLA;
- affected assets;
- support groups;
- knowledge base;
- ticket history and audit trail.

LibreNMS remains authoritative for live network state and monitoring evidence.

## 2. Profiles and roles

Recommended logical roles:

| Role | Purpose |
|---|---|
| Requester | Opens and follows own tickets |
| Technician L1 | First-line triage and common requests |
| Technician L2 Infrastructure | Servers, virtualization, storage, backup |
| Technician L2 Network | Cisco/MikroTik, connectivity, VLAN, routing |
| Security | Endpoint/security incidents |
| Service Desk Manager | Queue, SLA and escalation supervision |
| Approver | Request/change approval where required |
| GLPI Administrator | Platform administration only |

Avoid giving normal technicians administrative GLPI privileges.

## 3. Support groups

Suggested baseline groups:

```text
Service Desk L1
Infrastructure
Network
Security
Applications
Business Systems
Vendors / External Support
```

The final group structure should mirror actual operational ownership, not the organizational chart blindly.

## 4. Ticket taxonomy

Start with a controlled category tree.

```text
Incident
├── Network
│   ├── No connectivity
│   ├── Slow connectivity
│   ├── Wi-Fi
│   ├── VPN
│   ├── VLAN / Port
│   └── Network device
├── Endpoint
│   ├── Windows
│   ├── Hardware
│   ├── Printing
│   └── Security
├── Infrastructure
│   ├── Server
│   ├── Virtualization
│   ├── Storage
│   ├── Backup
│   └── UPS / Power
├── Application
└── Email

Request
├── Access
├── Account
├── Software installation
├── Hardware request
├── Network change
└── Other standard request
```

Do not create hundreds of categories initially. Expand only when reporting or routing requires it.

## 5. Priority model

Define priority based on Impact x Urgency.

Suggested interpretation:

| Impact | Description |
|---|---|
| High | Organization-wide or critical service |
| Medium | Department/group or important service |
| Low | Single user/device with workaround |

| Urgency | Description |
|---|---|
| High | Immediate operational impact |
| Medium | Work impaired but not stopped |
| Low | Can wait without material operational impact |

The resulting GLPI priority matrix should be reviewed and approved before production use.

## 6. SLA baseline

GLPI can track both TTO and TTR. Configure business calendars before defining production SLA values.

Example baseline:

| Priority | TTO | TTR |
|---|---:|---:|
| Critical | 15 min | 2 h |
| High | 30 min | 4 h |
| Medium | 4 h | 1 business day |
| Low | 1 business day | 3 business days |

Recommended calendars:

```text
Business Hours
  Monday-Friday
  08:00-17:00
  exclude holidays

24x7 Critical
  only if the organization actually provides 24x7 support
```

Do not configure a 24x7 SLA unless the support organization is staffed/on-call to meet it.

## 7. OLA model

Use OLA for internal commitments between groups.

Example:

```text
Service Desk L1
  TTO -> 15 minutes
  Escalate unresolved infrastructure/network issue to L2 within 30 minutes

Network Team
  OLA TTO -> 15 minutes after assignment
```

## 8. Ticket templates

Create templates for common processes.

### Network incident

Mandatory fields:

- requester;
- affected location;
- affected asset if known;
- category;
- impact;
- urgency;
- description;

Useful predefined fields:

```text
Category = Incident > Network
Group = Network
```

### Access request

Mandatory fields:

- requester;
- requested system;
- requested access level;
- business justification;
- approver.

### Change request

Mandatory fields:

- scope;
- implementation plan;
- rollback plan;
- impact;
- maintenance window;
- validation plan;
- approver.

## 9. Business rules

Recommended initial rules:

### Network

```text
IF category is under Incident > Network
THEN assign group Network
```

### Infrastructure

```text
IF category is under Incident > Infrastructure
THEN assign group Infrastructure
```

### Security

```text
IF category is under Incident > Endpoint > Security
THEN assign group Security
AND priority at least High
```

### Monitoring-originated incidents

```text
IF source/tag indicates LibreNMS
THEN assign according to affected object/category
AND add automation source metadata
```

## 10. Ticket-to-asset association

Whenever possible, incidents must be linked to the affected GLPI asset.

For an endpoint ticket, validate:

```text
Asset: HQ-PC-043
Serial: ABC123456
IP: 10.129.21.43
MAC: 00:25:90:AB:CD:EF
```

The integration layer can then use IP/MAC to obtain network context from LibreNMS.

## 11. Email collector

Email-to-ticket can be enabled after the core workflows are stable.

Recommended sequence:

1. Configure dedicated helpdesk mailbox.
2. Configure GLPI collector.
3. Test creation and follow-up behavior.
4. Add rules for sender/entity/category where justified.
5. Protect against mail loops and automated notification storms.
6. Document which email addresses generate tickets.

## 12. Knowledge base

Use resolved incidents to create reusable knowledge articles where appropriate.

Suggested categories:

```text
End User
Network/VPN
Windows
Email
Applications
Infrastructure Operations
Service Desk Internal
```

Separate end-user-visible articles from technician-only operational procedures.

## 13. Monitoring integration policy

Not every LibreNMS alert should become a ticket.

Good candidates:

- managed device down;
- critical uplink down;
- hardware component failure;
- persistent high interface errors;
- monitored core service failure.

Poor candidates unless heavily filtered:

- transient polling loss;
- every individual threshold fluctuation;
- informational events;
- low-value access port transitions.

Ticket creation must include deduplication and recovery correlation.

## 14. Pilot acceptance test

Perform at least these tests:

1. User opens a standard request.
2. L1 technician receives and owns it.
3. SLA TTO stops/calculates correctly after assignment.
4. Network incident routes to Network group.
5. Ticket is linked to an asset.
6. Technician can locate asset MAC/IP.
7. LibreNMS enrichment returns switch/port/VLAN.
8. SLA escalation notification is tested with an accelerated test SLA.
9. A monitoring test alert creates one incident only.
10. Recovery updates the same incident.

## 15. Production go-live checklist

- [ ] Roles and profiles reviewed.
- [ ] Support groups approved.
- [ ] Category taxonomy approved.
- [ ] Business calendar configured.
- [ ] SLA/OLA values approved.
- [ ] Notification templates reviewed.
- [ ] Automatic actions/cron verified.
- [ ] AD/LDAP pilot completed.
- [ ] Ticket templates validated.
- [ ] Asset linking validated.
- [ ] Monitoring integration tested.
- [ ] Backup/restore tested with Service Desk records.
- [ ] HTTPS/SSO/access controls enabled for production.
