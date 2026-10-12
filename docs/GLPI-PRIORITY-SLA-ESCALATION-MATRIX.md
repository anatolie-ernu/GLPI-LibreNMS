# GLPI Service Desk — Priority, SLA, OLA and Escalation Policy

## Status

**Stage 2 configuration source of truth**

This document defines the exact baseline to be configured in GLPI for the integrated Service Desk. It complements:

- `docs/GLPI-SERVICEDESK.md`
- `docs/GLPI-ESCALATION-REPORTING.md`
- `docs/STAGE-2-ITSM-SERVICEDESK.md`

The machine-readable companion is:

- `config/glpi/servicedesk-policy.yaml`
- `config/glpi/priority-matrix.csv`
- `config/glpi/sla-policies.csv`
- `config/glpi/support-groups.csv`
- `config/glpi/escalation-rules.csv`

The values below are the project baseline. They may be changed later only through an approved policy change.

---

## 1. Priority model

The organizational priority bands are:

| Code | Name | Meaning |
|---|---|---|
| P1 | Critical | Major business/service outage or severe security/availability event requiring immediate coordination |
| P2 | High | Significant operational impact, important service degraded, multiple users affected |
| P3 | Medium | Normal incident affecting a user/group with material but manageable impact |
| P4 | Low | Minor incident or low-risk request that can wait without material operational impact |

### 1.1 Impact definitions

| Impact | Definition |
|---|---|
| High | Organization-wide, critical service, core infrastructure, or multiple departments |
| Medium | One department, important service, multiple users, or an important shared asset |
| Low | One user/device or localized issue with limited business effect |

### 1.2 Urgency definitions

| Urgency | Definition |
|---|---|
| High | Work/service is stopped or immediate action is required |
| Medium | Work is impaired but can continue temporarily |
| Low | Workaround exists or delay has low operational consequence |

### 1.3 Impact × Urgency matrix

| Impact \ Urgency | High | Medium | Low |
|---|---|---|---|
| High | **P1 Critical** | **P2 High** | **P3 Medium** |
| Medium | **P2 High** | **P3 Medium** | **P4 Low** |
| Low | **P3 Medium** | **P4 Low** | **P4 Low** |

### 1.4 GLPI native priority mapping

GLPI can expose more native priority values than the four operational bands above. For reporting and SLA selection use this normalization:

| Operational band | GLPI priority mapping |
|---|---|
| P1 Critical | Major / Very High |
| P2 High | High |
| P3 Medium | Medium |
| P4 Low | Low / Very Low |

If the GLPI UI cannot rename native labels, retain native GLPI labels and use the P1-P4 mapping consistently in rules, documentation and reports.

### 1.5 Overrides

The matrix is the default. The following overrides are allowed:

- confirmed major incident -> P1;
- confirmed security incident with severe confidentiality/integrity/availability impact -> minimum P1/P2 according to security process;
- monitoring alert for core device/service down -> P1 or P2 according to service criticality;
- VIP/requester identity alone must **not** raise priority;
- standard access/software/hardware request must not become P1 solely because it is urgent to the requester.

---

## 2. Service calendars

### Business Hours

Baseline:

```text
Monday-Friday
08:00-17:00
Europe/Chisinau
Public holidays excluded
```

### Critical 24x7

Use only when an actual on-call/24x7 operating model exists.

Do not publish a 24x7 commitment if the organization cannot staff it.

---

## 3. SLA baseline

| Priority | TTO | TTR | Calendar | Escalation profile |
|---|---:|---:|---|---|
| P1 Critical | 15 min | 2 h | Critical 24x7 or approved critical calendar | P1 |
| P2 High | 30 min | 4 h | Business Hours | P2 |
| P3 Medium | 4 h | 1 business day | Business Hours | P3 |
| P4 Low | 1 business day | 3 business days | Business Hours | P4 |

Definitions:

- **TTO** — Time To Own / take into account.
- **TTR** — Time To Resolve.
- SLA clocks must use the configured GLPI calendars, not wall-clock approximations.

---

## 4. Support groups

### L0

```text
Self-Service / Knowledge Base
```

No technical ownership. Used to deflect known issues and standard requests.

### L1

```text
SD-L1-ServiceDesk
```

Responsibilities:

- receive/triage;
- classify impact and urgency;
- validate requester and affected asset;
- solve standard known issues;
- collect minimum diagnostics;
- escalate correctly to L2.

### L2

```text
SD-L2-Network
SD-L2-Infrastructure
SD-L2-Security
SD-L2-Applications
SD-L2-BusinessSystems
```

Responsibilities:

- specialist diagnosis and resolution;
- maintain technical worklog;
- invoke vendor/L3 where needed;
- create Problem candidates for recurrence.

### L3

```text
SD-L3-Senior
SD-L3-IT-Management
SD-L3-Vendor-Coordination
```

Responsibilities:

- senior technical escalation;
- major incident coordination;
- priority/resource decisions;
- vendor/escalation management;
- post-incident review ownership when required.

Management escalation does not automatically remove the current technical owner.

---

## 5. OLA baseline

| Group | OLA / target |
|---|---|
| SD-L1-ServiceDesk | acknowledge within 15 min for P1/P2 |
| SD-L1-ServiceDesk | functional handoff within 30 min when specialist ownership is required |
| SD-L2-* | acknowledge within 15 min after assignment for P1/P2 |
| SD-L2-* | acknowledge within 1 business hour after assignment for P3/P4 |
| SD-L3-Senior | acknowledge within 15 min for P1 |
| SD-L3-IT-Management | visibility immediately for P1 and at 75% TTR for P2 |
| SD-L3-Vendor-Coordination | engage vendor as soon as external dependency is confirmed |

OLA measures internal responsibility and must not silently replace the customer-facing SLA.

---

## 6. Functional routing rules

### Network

```text
IF category under Incident > Network
THEN group = SD-L2-Network
```

### Infrastructure

```text
IF category under Incident > Infrastructure
THEN group = SD-L2-Infrastructure
```

### Security

```text
IF category under Incident > Endpoint > Security
THEN group = SD-L2-Security
AND operational priority >= P2
```

### Applications

```text
IF category under Incident > Application
THEN group = SD-L2-Applications
```

### Business systems

```text
IF category under Incident > Business Systems
THEN group = SD-L2-BusinessSystems
```

### LibreNMS generated

```text
IF source = LibreNMS
THEN route by monitored object/category
AND preserve alert_id + device_id + rule_id correlation metadata
AND deduplicate before ticket creation
```

---

## 7. Concrete escalation rules

### P1 Critical — TTO 15 min / TTR 2 h

| Time/condition | Action |
|---|---|
| Creation | assign L1 plus relevant L2 when category is known; notify Service Desk Manager |
| 10 min and unowned | notify L1 lead + current specialist queue |
| 15 min TTO breach | notify Service Desk Manager + Head of IT; mark TTO breach |
| 30 min unresolved | notify L2 lead; require current action/update |
| 60 min (50% TTR) | escalate to SD-L3-Senior + Head of IT |
| 90 min (75% TTR) | engage SD-L3-Vendor-Coordination if external dependency exists; management visibility |
| 120 min TTR breach | breach notification; Major Incident review required; Problem record candidate |

### P2 High — TTO 30 min / TTR 4 h

| Time/condition | Action |
|---|---|
| Creation | assign L1 or direct L2 by category |
| 20 min and unowned | notify queue lead |
| 30 min TTO breach | notify Service Desk Manager |
| 2 h (50% TTR) | notify L2 lead |
| 3 h (75% TTR) | notify SD-L3-Senior / Head of IT visibility |
| 4 h TTR breach | management notification; review root cause/next action |

### P3 Medium — TTO 4 h / TTR 1 business day

| Time/condition | Action |
|---|---|
| Creation | L1 triage |
| 2 h and unowned | reminder to L1 queue |
| 4 h TTO breach | notify Service Desk Manager |
| 50% TTR | notify assigned group lead if unresolved |
| 75% TTR | escalation reminder and action-plan update |
| TTR breach | mark overdue and include in daily/weekly SLA report |

### P4 Low — TTO 1 business day / TTR 3 business days

| Time/condition | Action |
|---|---|
| Creation | L1 queue |
| 75% TTO | reminder to owner/queue |
| TTO breach | notify Service Desk queue lead |
| 2 business days unresolved | notify assigned group lead |
| 3 business days TTR breach | mark overdue and include in backlog aging report |

---

## 8. Major Incident rule

Default trigger:

```text
Impact = High
AND Urgency = High
=> P1 Critical
=> Major Incident process
```

Also permit manual promotion to Major Incident by authorized roles.

Required actions:

- Major Incident coordinator assigned;
- Head of IT notified;
- affected service/assets identified;
- related tickets linked where practical;
- technical owner retained;
- periodic status updates;
- restore timestamp recorded;
- Problem/RCA decision recorded;
- post-incident review for selected P1 incidents.

---

## 9. Pending policy

Use explicit reasons:

```text
Waiting for requester
Waiting for vendor
Waiting for approval
Waiting for maintenance window
Waiting for external dependency
```

Baseline behavior:

| Pending reason | TTR handling |
|---|---|
| Waiting for requester | may pause if approved by Service Desk policy |
| Waiting for approval | may pause for service requests where approval is mandatory |
| Waiting for maintenance window | may pause only when the planned window is valid and documented |
| Waiting for vendor | customer SLA continues by default; track vendor OLA/contract separately |
| External dependency | customer SLA continues by default unless the service contract explicitly excludes it |

Never use Pending merely to hide SLA breaches.

---

## 10. Required ticket fields

For incidents:

- requester;
- entity/department;
- category;
- impact;
- urgency;
- calculated/normalized priority;
- affected asset where known;
- location;
- assigned group;
- SLA;
- source;
- description;
- latest action/worklog.

For P1/P2 additionally:

- business impact statement;
- current owner;
- next action;
- next update time;
- major incident flag where applicable.

---

## 11. Reporting dimensions

Minimum filters/dimensions:

- priority P1-P4;
- GLPI native priority;
- status;
- category;
- support level;
- assigned group;
- technician;
- entity/department;
- location;
- affected asset;
- source (user/email/LibreNMS/API);
- SLA TTO compliant/breached;
- SLA TTR compliant/breached;
- escalation level reached;
- major incident;
- vendor involvement.

Minimum KPIs:

- opened / solved / closed;
- backlog and aging;
- TTO/MTTA;
- TTR/MTTR;
- SLA compliance;
- breach count;
- FCR;
- reopen rate;
- escalations L1->L2 and L2->L3;
- P1/P2 volume;
- repeated incidents;
- top affected assets;
- customer satisfaction;
- LibreNMS alert-to-ticket conversion and duplicate suppression.

---

## 12. GLPI implementation order

1. Create calendars.
2. Create L1/L2/L3 support groups.
3. Create/validate technician profiles and permissions.
4. Create category tree.
5. Configure Impact/Urgency priority calculation/mapping.
6. Create P1-P4 SLA definitions.
7. Create OLA definitions.
8. Create ticket templates.
9. Create assignment/routing rules.
10. Create time-based escalation levels.
11. Configure notifications.
12. Configure dashboards/reports.
13. Run accelerated test SLA cases.
14. Run normal pilot.
15. Approve production values.

---

## 13. Acceptance tests

### Priority

- High impact + High urgency -> P1.
- High impact + Medium urgency -> P2.
- Medium impact + Medium urgency -> P3.
- Low impact + Low urgency -> P4.

### Routing

- Network ticket -> SD-L2-Network.
- Infrastructure ticket -> SD-L2-Infrastructure.
- Security ticket -> SD-L2-Security and minimum P2.
- Application ticket -> SD-L2-Applications.

### Escalation

- accelerated P1 reaches 50%/75%/breach actions exactly once;
- TTO breach does not create duplicate notifications every cron cycle;
- management escalation does not clear technical assignment;
- Pending behavior matches the approved reason policy.

### Reporting

- SLA TTO/TTR compliance can be reported by group/category/month;
- escalation level can be reported;
- P1/P2 trend is visible;
- asset-centric ticket counts are available;
- LibreNMS-originated tickets are identifiable.

