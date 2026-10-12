#!/usr/bin/env python3
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "glpi"

VALID = {"P1", "P2", "P3", "P4"}
errors: list[str] = []

def rows(name: str):
    path = CFG / name
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

matrix = rows("priority-matrix.csv")
sla = rows("sla-policies.csv")
groups = rows("support-groups.csv")
escalations = rows("escalation-rules.csv")

# Matrix: all 3x3 combinations once.
expected_pairs = {(i, u) for i in ("High", "Medium", "Low") for u in ("High", "Medium", "Low")}
actual_pairs = {(r.get("impact"), r.get("urgency")) for r in matrix}
if len(matrix) != 9:
    errors.append(f"priority-matrix.csv must contain 9 rows, found {len(matrix)}")
if actual_pairs != expected_pairs:
    errors.append("priority-matrix.csv does not contain every Impact x Urgency combination exactly once")
for r in matrix:
    if r.get("priority_code") not in VALID:
        errors.append(f"invalid matrix priority: {r}")

# SLA: one row per P level.
sla_codes = [r.get("priority_code") for r in sla]
if set(sla_codes) != VALID or len(sla_codes) != 4:
    errors.append(f"sla-policies.csv must define exactly P1-P4 once; found {sla_codes}")

# Groups: required operational groups.
required_groups = {
    "Self-Service-KB",
    "SD-L1-ServiceDesk",
    "SD-L2-Network",
    "SD-L2-Infrastructure",
    "SD-L2-Security",
    "SD-L2-Applications",
    "SD-L2-BusinessSystems",
    "SD-L3-Senior",
    "SD-L3-IT-Management",
    "SD-L3-Vendor-Coordination",
}
actual_groups = {r.get("group_name") for r in groups}
missing_groups = required_groups - actual_groups
if missing_groups:
    errors.append("missing support groups: " + ", ".join(sorted(missing_groups)))

# Escalations reference only known priority bands.
for r in escalations:
    if r.get("priority") not in VALID:
        errors.append(f"invalid escalation priority: {r}")

# YAML is deliberately validated with stdlib-only structural checks.
yaml_path = CFG / "servicedesk-policy.yaml"
if not yaml_path.exists():
    errors.append("missing config/glpi/servicedesk-policy.yaml")
else:
    text = yaml_path.read_text(encoding="utf-8")
    for token in (
        "priority_bands:",
        "impact_urgency_matrix:",
        "calendars:",
        "groups:",
        "routing:",
        "pending_policy:",
        "reporting:",
    ):
        if token not in text:
            errors.append(f"servicedesk-policy.yaml missing section {token}")
    for code in sorted(VALID):
        if not re.search(rf"(?m)^\s{{2}}{code}:\s*$", text):
            errors.append(f"servicedesk-policy.yaml missing priority band {code}")

if errors:
    print("Service Desk policy validation FAILED:")
    for e in errors:
        print(f" - {e}")
    sys.exit(1)

print("Service Desk policy validation PASSED")
print(f" - matrix rows: {len(matrix)}")
print(f" - SLA policies: {len(sla)}")
print(f" - support groups: {len(groups)}")
print(f" - escalation rules: {len(escalations)}")
