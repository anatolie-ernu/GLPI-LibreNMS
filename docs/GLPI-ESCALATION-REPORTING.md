# GLPI Service Desk — Escalation, KPI and Reporting Model

## Purpose

Define a production-ready escalation and reporting model for the integrated GLPI Service Desk.

The model assumes:

```text
GLPI = Service Desk / ITSM + CMDB + Assets
LibreNMS = Network Monitoring / Discovery
Integration API = automation and network enrichment
```

## 1. Escalation model

Use two complementary escalation dimensions:

1. **Functional escalation** — move the ticket to a more specialized support level.
2. **Hierarchical escalation** — notify or involve management when SLA/risk thresholds are reached.

### Recommended support levels

```text
L0  Self-Service / Knowledge Base
 |
 v
L1  Service Desk
 |
 +--> L2 Network
 |
 +--> L2 Infrastructure
 |
 +--> L2 Security
 |
 +--> L2 Applications
 |
 v
L3  Senior Specialist / Head of IT / Vendor
```

Do not use escalation levels merely as organizational ranks. Each level must correspond to a concrete operational capability or decision authority.

## 2. Example escalation matrix

| Level | Trigger | Typical action |
|---|---|---|
| L1 | New ticket | Assign Service Desk, start TTO |
| L2 | L1 cannot resolve / category-specific rule | Assign specialist group |
| L2 urgent | 50% of TTR consumed | Notify group lead, increase visibility |
| L3 | 75% of TTR consumed or major incident | Notify Head of IT / senior specialist |
| Breach | TTR expired | Mark/escalate priority, management notification |
| Vendor | External dependency identified | Assign/notify vendor coordination group |

## 3. Time-based escalation example

For a High-priority incident with TTR = 4 hours:

```text
00:00  Ticket created
       SLA starts

00:15  If still New
       -> assign L1 group
       -> notify L1 queue

00:30  TTO deadline
       If still unowned
       -> Priority = Very High
       -> notify Service Desk Manager

02:00  50% TTR
       If unresolved
       -> notify current group lead
       -> add escalation tag

03:00  75% TTR
       If unresolved
       -> notify Head of IT / L3
       -> require action plan update

04:00  TTR breach
       -> breach notification
       -> management escalation
       -> mandatory post-resolution review for selected categories
```

GLPI escalation levels can be placed before or after SLA/OLA TTO/TTR deadlines and can execute rule actions based on ticket criteria.

## 4. Functional escalation rules

### Network

```text
IF Category under Incident > Network
THEN Group = Network
```

### Infrastructure

```text
IF Category under Incident > Infrastructure
THEN Group = Infrastructure
```

### Security

```text
IF Category under Incident > Endpoint > Security
THEN Group = Security
AND Priority >= High
```

### Major outage

```text
IF Impact = High
AND Urgency = High
THEN Priority = Critical
AND notify Service Desk Manager
AND notify Head of IT
```

## 5. Hierarchical escalation

Recommended management escalation:

```text
Technician
    |
Group Lead
    |
Service Desk Manager / Senior Specialist
    |
Head of IT
    |
External Vendor / Management where required
```

Hierarchical escalation should not automatically remove the original technical owner. Management escalation is primarily for visibility, decision-making, prioritization and resource allocation.

## 6. OLA between support groups

Example internal flow:

```text
L1 Service Desk
  OLA TTO: 15 min
  OLA handoff target: 30 min

Network L2
  OLA TTO after assignment: 15 min

Infrastructure L2
  OLA TTO after assignment: 15 min
```

This provides internal accountability without changing the customer-facing SLA.

## 7. Pending status policy

GLPI can suspend/recalculate SLA timing while tickets are Pending depending on service-level behavior.

Define explicit pending reasons:

```text
Waiting for requester
Waiting for vendor
Waiting for maintenance window
Waiting for approval
Waiting for external dependency
```

Avoid using Pending simply to stop SLA timers without a valid operational reason.

## 8. Major incident model

Create a dedicated Major Incident process for high-impact outages.

Suggested trigger:

```text
Impact = High
AND Urgency = High
```

Additional requirements:

- assign Major Incident coordinator;
- notify Head of IT;
- identify affected assets/services;
- link related tickets where practical;
- maintain periodic status updates;
- capture start/restore/close timestamps;
- create Problem record for root cause analysis when appropriate;
- perform post-incident review.

## 9. Reports — native GLPI baseline

GLPI native ticket statistics can report:

- tickets opened;
- tickets solved;
- late tickets;
- tickets closed;
- average processing/take-into-account time;
- average resolution time;
- average closure time;
- real technician duration;
- satisfaction survey count and average satisfaction;
- statistics by requester;
- statistics by assigned technician/group;
- statistics by impact/category;
- statistics by hardware/assets associated with tickets.

## 10. Recommended management dashboard

### Executive / Head of IT dashboard

```text
Open tickets by priority
SLA compliance %
SLA breaches
Critical/High incidents
Mean Time To Own
Mean Time To Resolve
Backlog trend
Tickets by department
Tickets by service/category
Top recurring problems
Major incidents this month
Customer satisfaction
```

### Service Desk Manager dashboard

```text
New / Assigned / Pending / Solved
Unassigned tickets
Tickets approaching TTO
Tickets approaching TTR
Overdue tickets
Tickets per technician
Tickets per support group
Reopened tickets
Oldest open tickets
First-line resolution rate
```

### Network dashboard

Combine GLPI and LibreNMS metrics:

```text
Network incidents open
Network SLA compliance
Incidents by site/VLAN/device
Switch/device availability
Top interfaces by errors
Device-down alerts converted to incidents
Repeated incidents per switch/port
Top endpoints with connectivity incidents
```

### Infrastructure dashboard

```text
Server incidents
Virtualization incidents
Backup incidents
Storage incidents
Critical infrastructure SLA
Repeated incidents by asset
```

## 11. Core KPIs

### Ticket volume

```text
Tickets opened / day / week / month
Tickets closed / day / week / month
Net backlog change = opened - closed
```

### SLA compliance

```text
SLA TTO compliance %
SLA TTR compliance %
Number of TTO breaches
Number of TTR breaches
```

### MTTA / TTO

Measure time from ticket creation to first ownership/action.

### MTTR

Measure time from incident creation to resolution.

Use separate reporting for:

- all incidents;
- Critical/High only;
- Network;
- Infrastructure;
- Security;
- Applications.

### First-line resolution rate

```text
Tickets solved by L1 without escalation
--------------------------------------- x 100
Total tickets handled by L1
```

### Reopen rate

```text
Reopened tickets / solved tickets * 100
```

### Backlog aging

Suggested buckets:

```text
< 1 day
1-3 days
4-7 days
8-14 days
15-30 days
> 30 days
```

### Recurrence

Track categories/assets with repeated incidents to identify candidates for Problem Management.

## 12. Asset-centric reporting

Because Service Desk and CMDB are both in GLPI, report directly against affected assets:

```text
Top computers by ticket count
Top network devices by incident count
Tickets by hardware model
Tickets by OS/version
Tickets by location
Tickets by department
Tickets by asset lifecycle state
```

This is one of the primary advantages of using GLPI Service Desk instead of a separate ticketing platform.

## 13. LibreNMS + GLPI combined reporting

The Integration API should store enough correlation metadata to support reports such as:

```text
LibreNMS alerts -> GLPI incidents
Alert-to-ticket conversion count
Duplicate alerts suppressed
Recovery-to-resolution time
Top devices creating incidents
Top ports involved in user incidents
Device availability vs incident count
```

Do not duplicate all LibreNMS time-series data inside GLPI. Store references/correlation metadata and query LibreNMS for network metrics when needed.

## 14. Scheduled reporting

Recommended recurring reports:

### Daily operations

Recipients: Service Desk / IT operations

```text
Critical and High open tickets
SLA breaches in last 24h
Tickets due today
Unassigned tickets
Major monitoring incidents
```

### Weekly IT operations report

Recipients: Head of IT + team leads

```text
Tickets opened/closed
Backlog change
SLA TTO/TTR compliance
Top categories
Top affected assets
Escalations by level
Major incidents
Repeated incidents
LibreNMS device/alert summary
Risks/actions for next week
```

### Monthly management report

```text
Ticket trend
SLA compliance trend
MTTA/MTTR trend
Incident distribution by department/service
Top recurring problems
Major incidents and business impact
Asset reliability patterns
Customer satisfaction
Vendor-related delays
Improvement actions
```

## 15. Dashboard access model

Create dashboards by audience:

```text
End User
Technician
Support Group Lead
Service Desk Manager
Head of IT
Management
```

GLPI dashboards can be filtered and shared with users, groups, profiles or entities. Do not expose operational/security-sensitive dashboards through public links unless explicitly approved.

## 16. Reporting retention

Define retention for:

- tickets and historical changes;
- satisfaction data;
- correlation records;
- audit logs;
- LibreNMS RRD/time-series data;
- exported management reports.

Retention should follow organizational/legal requirements rather than arbitrary application defaults.

## 17. Stage 2 acceptance criteria — escalation/reporting

- [ ] L1 -> L2 functional escalation tested.
- [ ] L2 -> L3/management escalation tested.
- [ ] TTO pre-deadline escalation tested.
- [ ] TTR pre-deadline escalation tested.
- [ ] TTR breach escalation tested.
- [ ] OLA between at least two internal groups tested.
- [ ] Pending reason/timer behavior validated.
- [ ] Major Incident workflow defined.
- [ ] Service Desk Manager dashboard created.
- [ ] Head of IT dashboard created.
- [ ] SLA compliance report validated.
- [ ] Weekly ITSM report definition approved.
- [ ] Asset-centric ticket reporting validated.
- [ ] LibreNMS alert-to-ticket reporting available after integration implementation.
