# GLPI Service Desk configuration source of truth

This directory contains the approved baseline for Stage 2 Service Desk configuration.

Files:

- `servicedesk-policy.yaml` — canonical machine-readable policy.
- `priority-matrix.csv` — Impact x Urgency -> P1-P4.
- `sla-policies.csv` — TTO/TTR/calendar values.
- `support-groups.csv` — L0/L1/L2/L3 group structure.
- `escalation-rules.csv` — time-based escalation actions.

## Important

These files are **configuration specifications**, not proof that the settings are already active inside a running GLPI instance.

Apply and validate them in GLPI according to:

- `docs/GLPI-PRIORITY-SLA-ESCALATION-MATRIX.md`
- `docs/GLPI-SERVICEDESK.md`
- `docs/GLPI-ESCALATION-REPORTING.md`

After implementation, record evidence/screenshots or exported configuration in a separate evidence directory rather than storing credentials in Git.

## Change control

Any production change to priority, SLA, OLA or escalation policy should update the YAML/CSV files first so Git remains the configuration source of truth.
