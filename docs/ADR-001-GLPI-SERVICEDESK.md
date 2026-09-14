# ADR-001 — Use GLPI as the Integrated Service Desk

- **Status:** Accepted
- **Date:** 2026-09-14
- **Decision owner:** Project architecture

## Context

The platform already uses GLPI as the asset inventory and CMDB layer and LibreNMS as the network monitoring/discovery layer. A separate Service Desk product would introduce an additional user directory, ticket database, permissions model, API integration surface, backup scope and lifecycle to operate.

The required ITSM functions are available in GLPI and are directly adjacent to the asset/CMDB data that Service Desk technicians need.

## Decision

Use **GLPI Service Desk / Assistance** as the project's authoritative ITSM platform.

The production architecture is therefore:

```text
Active Directory / LDAP
          |
          v
+--------------------------------------+
|                 GLPI                 |
|                                      |
|  Service Desk / ITSM                 |
|  - Incidents                         |
|  - Requests                          |
|  - Problems                          |
|  - Changes                           |
|  - SLA / OLA                         |
|  - Knowledge Base                    |
|                                      |
|  CMDB / Assets                       |
|  - Computers                         |
|  - Servers                           |
|  - Network devices                   |
|  - Users / locations                 |
+------------------+-------------------+
                   |
                   | asset IP/MAC
                   v
          Integration API
                   |
                   v
+--------------------------------------+
|              LibreNMS                |
| Monitoring / FDB / VLAN / LLDP/CDP   |
| Cisco + MikroTik                     |
+--------------------------------------+
```

## Consequences

### Positive

- One user-facing Service Desk platform.
- Tickets can be linked directly to GLPI assets.
- No asset synchronization between a separate Service Desk and GLPI.
- AD/LDAP integration is centralized in GLPI for the ITSM workflow.
- SLA/OLA, business rules and ticket templates remain in the same system.
- Backup and recovery scope is simpler.
- Fewer application stacks and databases to maintain.
- LibreNMS integration only needs to enrich GLPI and create/update GLPI tickets.

### Trade-offs

- Service Desk UX and workflows are constrained to GLPI capabilities and extensions.
- Changes to GLPI affect both CMDB/asset and ITSM services, increasing the importance of staging and backups.
- API automation must be carefully permission-scoped because GLPI contains both asset and Service Desk data.

## Rejected alternative

A separate Service Desk such as Zammad is not part of the baseline architecture.

It may be reconsidered only if a future requirement cannot be met adequately by GLPI, for example a mandatory omnichannel/contact-center workflow that justifies the additional integration and operational complexity.

## Implementation rule

All Stage 2 work must assume:

```text
GLPI = CMDB + Asset Management + Service Desk / ITSM
LibreNMS = Network Monitoring + Discovery
Integration API = controlled correlation and automation layer
```

Do not duplicate ticketing, asset or identity ownership in another platform without a new architecture decision record.
