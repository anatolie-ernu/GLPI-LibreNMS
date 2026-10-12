# GLPI Stage 2 Configuration Runbook

## Purpose

Apply the repository Service Desk source-of-truth consistently to a GLPI 11 environment.

Policy sources:

- `config/glpi/servicedesk-policy.yaml`
- `config/glpi/priority-matrix.csv`
- `config/glpi/sla-policies.csv`
- `config/glpi/support-groups.csv`
- `config/glpi/escalation-rules.csv`
- `docs/GLPI-PRIORITY-SLA-ESCALATION-MATRIX.md`

This runbook is intentionally environment-neutral. Do not put production LDAP passwords, API tokens or private addresses in Git.

---

## 0. Pre-change checklist

Before changing GLPI:

- take a database/application backup;
- confirm the target entity;
- confirm mail/notification test recipient;
- confirm GLPI automatic actions/cron are operational;
- identify pilot requester and pilot technicians;
- choose an accelerated test window before using production SLA durations.

---

## 1. Create Service Desk groups

GLPI path:

```text
Administration > Groups
```

Create:

```text
SD-L1-ServiceDesk
SD-L2-Network
SD-L2-Infrastructure
SD-L2-Security
SD-L2-Applications
SD-L2-BusinessSystems
SD-L3-Senior
SD-L3-IT-Management
SD-L3-Vendor-Coordination
```

For every group validate:

- correct entity;
- visibility/recursion as required;
- technician members;
- group manager/lead where appropriate;
- notification scope.

Do not make every imported AD group a Service Desk assignment group. Import/map only operationally useful groups.

---

## 2. Configure LDAP / Active Directory pilot

GLPI path:

```text
Configuration (Setup) > Authentication > LDAP directories
```

Pilot sequence:

1. Add the AD/LDAP directory.
2. Use LDAPS/TLS where supported by the environment.
3. Test directory connectivity.
4. Configure user login attribute and base DN.
5. Configure group discovery.
6. Import/synchronize only pilot users/groups first.
7. Map authorization/profile/entity deliberately.
8. Test disabled-user behavior.
9. Test nested group membership if used.

Groups can then be imported through:

```text
Administration > Groups > LDAP directory link
```

Do not store bind passwords in repository files.

---

## 3. Configure categories

Create the controlled category tree from `docs/GLPI-SERVICEDESK.md`.

Minimum incident tree:

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
├── Business Systems
└── Email
```

Minimum request tree:

```text
Request
├── Access
├── Account
├── Software installation
├── Hardware request
├── Network change
└── Other standard request
```

Avoid uncontrolled category proliferation.

---

## 4. Configure calendars

Create:

### Business-Hours

```text
Monday-Friday
08:00-17:00
Timezone: Europe/Chisinau
Exclude approved public holidays
```

### Critical-24x7

Create/use only if an actual on-call/24x7 service exists.

A GLPI SLA/OLA should be linked to the appropriate calendar. If no calendar is associated, GLPI can calculate continuously, so calendar assignment must be explicitly verified.

---

## 5. Configure Impact x Urgency policy

Use `config/glpi/priority-matrix.csv`.

Expected results:

```text
High + High     -> P1 Critical
High + Medium   -> P2 High
High + Low      -> P3 Medium

Medium + High   -> P2 High
Medium + Medium -> P3 Medium
Medium + Low    -> P4 Low

Low + High      -> P3 Medium
Low + Medium    -> P4 Low
Low + Low       -> P4 Low
```

GLPI may expose native labels such as Major/Very High/High/Medium/Low/Very Low. Preserve the repository operational P1-P4 normalization for SLA selection and reporting.

Test all nine matrix combinations.

---

## 6. Create SLA definitions

GLPI Service Levels support TTO and TTR.

Create the following production baseline after accelerated tests:

### SLA-P1-Critical

```text
TTO: 15 minutes
TTR: 2 hours
Calendar: Critical-24x7 or approved critical calendar
```

### SLA-P2-High

```text
TTO: 30 minutes
TTR: 4 hours
Calendar: Business-Hours
```

### SLA-P3-Medium

```text
TTO: 4 hours
TTR: 1 business day
Calendar: Business-Hours
```

### SLA-P4-Low

```text
TTO: 1 business day
TTR: 3 business days
Calendar: Business-Hours
```

Verify the due dates on a test ticket before proceeding.

---

## 7. Create OLA definitions

Create internal targets:

```text
OLA-L1-P1P2-Acknowledge     15 min
OLA-L1-Specialist-Handoff   30 min
OLA-L2-P1P2-Acknowledge     15 min after assignment
OLA-L2-P3P4-Acknowledge     1 business hour after assignment
OLA-L3-P1-Acknowledge       15 min
```

OLA is internal accountability. It must not silently replace the requester/customer SLA.

---

## 8. Create ticket templates

GLPI can assign SLA fields from ticket templates.

Create at minimum:

### TPL-Incident-Network

Mandatory:

- requester;
- location;
- affected asset if known;
- category;
- impact;
- urgency;
- description.

### TPL-Incident-Infrastructure

Mandatory:

- affected service/asset;
- impact;
- urgency;
- symptoms;
- last known good state.

### TPL-Incident-Security

Mandatory:

- affected endpoint/account/service;
- detection source;
- impact;
- urgency;
- evidence/reference.

### TPL-Request-Access

Mandatory:

- requester;
- system;
- requested access;
- justification;
- approver.

### TPL-Change

Mandatory:

- scope;
- implementation plan;
- rollback plan;
- impact;
- maintenance window;
- validation plan;
- approver.

---

## 9. Create business rules for tickets

GLPI path:

```text
Administration > Rules
```

Use Business rules for tickets.

Create deterministic ordering.

### BR-010 Network routing

Criteria:

```text
Category under Incident > Network
```

Actions:

```text
Assigned group = SD-L2-Network
```

### BR-020 Infrastructure routing

```text
Category under Incident > Infrastructure
=> SD-L2-Infrastructure
```

### BR-030 Security routing

```text
Category under Incident > Endpoint > Security
=> SD-L2-Security
=> minimum operational priority P2
```

### BR-040 Application routing

```text
Category under Incident > Application
=> SD-L2-Applications
```

### BR-050 Business Systems routing

```text
Category under Incident > Business Systems
=> SD-L2-BusinessSystems
```

### BR-100 Major Incident

```text
Impact = High
AND Urgency = High
=> P1 Critical
=> management visibility
=> Major Incident workflow
```

### BR-200 LibreNMS source

```text
Source/automation metadata = LibreNMS
=> route by monitored object/category
=> preserve correlation metadata
```

Integration API deduplication must occur before creating repeated tickets.

---

## 10. Assign SLA

Use one or more of:

- Business rules for tickets;
- ticket templates;
- manual assignment for controlled exceptions.

Mapping:

```text
P1 -> SLA-P1-Critical
P2 -> SLA-P2-High
P3 -> SLA-P3-Medium
P4 -> SLA-P4-Low
```

Create a test case for every mapping.

---

## 11. Configure escalation levels

GLPI permits escalation levels before or after SLA/OLA deadlines with criteria and actions.

Use `config/glpi/escalation-rules.csv`.

### P1

```text
10m unowned       -> queue/lead reminder
15m TTO breach    -> Service Desk Manager + Head of IT
30m unresolved    -> L2 lead/action update
60m 50% TTR       -> L3 Senior + Head of IT
90m 75% TTR       -> management/vendor visibility
120m breach       -> breach + Major Incident review + Problem candidate
```

### P2

```text
20m unowned
30m TTO breach
2h 50% TTR
3h 75% TTR
4h breach
```

### P3

```text
2h unowned
4h TTO breach
50% TTR
75% TTR
1 business day breach
```

### P4

```text
75% TTO reminder
1 business day TTO breach
2 business days unresolved
3 business days TTR breach
```

Criteria should ensure each escalation action is meaningful and not repeatedly noisy.

---

## 12. Configure SLA automatic actions and notifications

Verify automatic actions/cron.

Relevant GLPI automatic action:

```text
Setup > Automatic actions > slaticket
```

Verify notification configuration, including Ticket Recall/reminder recipients.

Use a test mailbox/group before enabling management-wide notifications.

---

## 13. Pending behavior

Use explicit pending reasons:

- Waiting for requester;
- Waiting for vendor;
- Waiting for approval;
- Waiting for maintenance window;
- Waiting for external dependency.

Baseline:

- requester/mandatory approval/valid maintenance window may pause according to approved policy;
- vendor/external dependency does not pause customer SLA by default;
- never use Pending solely to hide a breach.

GLPI recalculates TTR around Pending status, so test this behavior with the configured service level.

---

## 14. Dashboards and reports

Create audience-specific views.

### Service Desk Manager

- New/Assigned/Pending;
- unassigned;
- approaching TTO/TTR;
- overdue;
- tickets per group/technician;
- oldest tickets;
- FCR;
- reopen rate.

### Head of IT

- P1/P2 open;
- SLA compliance;
- TTO/MTTA;
- TTR/MTTR;
- backlog trend;
- escalation level reached;
- Major Incidents;
- repeated incidents;
- top affected assets;
- satisfaction.

### Network

- network incidents;
- SLA compliance;
- incidents per device/site/VLAN;
- LibreNMS alert-to-ticket count;
- repeated incidents by switch/port.

---

## 15. Accelerated test plan

Before production durations, create temporary SLA values such as:

```text
P1-test TTO 2 min / TTR 8 min
P2-test TTO 3 min / TTR 12 min
```

Validate:

1. assignment stops TTO as expected;
2. pre-deadline escalation runs once;
3. TTO breach notification works;
4. 50%/75% TTR escalation works;
5. Pending behavior is correct;
6. TTR breach is visible in statistics;
7. management escalation does not remove technical ownership;
8. cron/automatic action execution is reliable.

Delete/disable test SLAs after evidence is captured.

---

## 16. Production acceptance

Production baseline is accepted only when:

- all nine Impact/Urgency combinations pass;
- all P1-P4 SLA mappings pass;
- L1/L2/L3 routing passes;
- accelerated escalations pass;
- Pending behavior is approved;
- Service Desk Manager report is usable;
- Head of IT report is usable;
- backup/restore retains Service Desk records;
- AD/LDAP pilot passes;
- no production credentials are committed to Git.

## Official GLPI references

- Service Levels: https://help.glpi-project.org/documentation/modules/configuration/service_levels
- SLA FAQ: https://help.glpi-project.org/faq/glpi/service_levels
- Groups: https://help.glpi-project.org/faq/glpi/groups_users
- Rules: https://help.glpi-project.org/faq/glpi/rules
- LDAP: https://help.glpi-project.org/documentation/modules/configuration/authentication/ldap
