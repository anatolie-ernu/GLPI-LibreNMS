# Stage 2 Implementation Status

Last reviewed against repository `main`: October 2026.

## Status legend

- **Implemented in code/config** — deployable artifact exists in repository.
- **Specified** — documented/configured as source of truth, but still requires application inside GLPI or coding.
- **Planned** — architecture/backlog exists, implementation not yet present.

## Current state

| Capability | Status | Repository evidence |
|---|---|---|
| Canonical hardened Docker stack | Implemented in code/config | `docker-compose.yml`, `.env.example`, installer/config scripts |
| Nginx Proxy Manager | Implemented in code/config | `docker-compose.yml`, installer/configuration docs |
| Production hardening / Compose consolidation | Implemented in code/config | `docs/PRODUCTION-HARDENING.md`, legacy `compose.yml` removed |
| NPM auto-discovery | Implemented in code/config, opt-in | `npm-auto-discovery.py`, `Dockerfile.discovery`, Docker Socket Proxy profile |
| Cisco SNMPv3 baseline | Specified | `docs/CISCO-SNMPV3.md`, `config/cisco/` |
| MikroTik SNMPv3 baseline | Specified | `docs/MIKROTIK-SNMPV3.md`, `config/mikrotik/` |
| GLPI Agent rollout | Specified | `docs/GLPI-AGENT.md` |
| GLPI Service Desk operating model | Specified | `docs/GLPI-SERVICEDESK.md` |
| Service Desk architecture decision | Specified/approved | `docs/ADR-001-GLPI-SERVICEDESK.md` |
| Escalation/reporting model | Specified | `docs/GLPI-ESCALATION-REPORTING.md` |
| Impact x Urgency matrix | Specified as source of truth | `config/glpi/priority-matrix.csv` |
| P1-P4 SLA baseline | Specified as source of truth | `config/glpi/sla-policies.csv` |
| L0/L1/L2/L3 groups | Specified as source of truth | `config/glpi/support-groups.csv` |
| Concrete escalation rules | Specified as source of truth | `config/glpi/escalation-rules.csv` |
| Canonical Service Desk policy | Specified as source of truth | `config/glpi/servicedesk-policy.yaml` |
| Stage 2 GLPI configuration runbook | Implemented documentation | `docs/GLPI-STAGE2-CONFIGURATION-RUNBOOK.md` |
| Service Desk policy CI validator | Implemented in code/config | `scripts/validate-servicedesk-policy.py`, `.github/workflows/validate.yml` |
| Integration API design | Specified | `integration-api/README.md` |
| Integration API OpenAPI contract | Specified | `integration-api/openapi.yaml` |
| Integration API executable service | Implemented in code/config; pilot validation required | `integration-api/app/`, `integration-api/Dockerfile`, Compose `integration` profile |
| LibreNMS -> GLPI automatic ticket creation | Implemented in code/config; pilot validation required | `integration-api/app/service.py`, `integration-api/app/glpi.py` |
| Alert deduplication/recovery correlation | Implemented in code/config; pilot validation required | SQLite correlation store + unit tests |
| AD/LDAP pilot configuration | **Planned for deployment** | procedure documented, no environment-specific secrets/config committed |
| GLPI dashboard configuration | **Planned for deployment** | KPIs/dashboard definitions documented |
| Automated GLPI policy provisioning | **Planned** | YAML/CSV source exists; no provisioning script yet |
| PDF/Word ERNU.EU documentation | Implemented | repository DOCX/PDF documentation and PDF workflow |

## Next implementation sequence

1. Apply L0/L1/L2/L3 groups in a GLPI pilot.
2. Configure calendars.
3. Configure priority calculation and P1-P4 normalization.
4. Configure SLA/OLA.
5. Configure ticket templates and business routing rules.
6. Configure time-based escalation levels and notifications.
7. Configure Service Desk Manager and Head of IT dashboards.
8. Perform accelerated SLA tests.
9. Configure AD/LDAP pilot.
10. Configure Integration API credentials in the pilot environment.
11. Validate LibreNMS enrichment and alert-to-ticket workflow against live pilot systems.
12. Add end-to-end deployment evidence and decide whether to migrate GLPI writes to API v2.

## Definition of Stage 2 complete

Stage 2 is not complete merely because documentation exists. Completion requires evidence that the configured GLPI instance passes the acceptance tests in:

- `docs/GLPI-PRIORITY-SLA-ESCALATION-MATRIX.md`
- `docs/STAGE-2-ITSM-SERVICEDESK.md`
- `docs/GLPI-ESCALATION-REPORTING.md`
