from __future__ import annotations

import ipaddress
import re

from .models import LibreNmsEvent

_HEX = re.compile(r"[^0-9a-fA-F]")


def normalize_mac(value: str) -> str:
    compact = _HEX.sub("", value).lower()
    if len(compact) != 12 or not all(ch in "0123456789abcdef" for ch in compact):
        raise ValueError("invalid MAC address")
    return compact


def display_mac(value: str) -> str:
    compact = normalize_mac(value)
    return ":".join(compact[i : i + 2] for i in range(0, 12, 2))


def normalize_ip(value: str) -> str:
    return str(ipaddress.ip_address(value))


def correlation_key(event: LibreNmsEvent) -> str:
    fault = (event.fault_object or "device").strip().replace(":", "_")[:160]
    return f"librenms:{event.device_id}:{event.rule_id}:{fault}"


def is_recovery_state(value: str | int | bool) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value == 0
    normalized = str(value).strip().lower()
    return normalized in {
        "0",
        "ok",
        "clear",
        "cleared",
        "recover",
        "recovered",
        "resolved",
        "closed",
    }


def severity_to_glpi_priority(severity: str | None) -> int:
    value = (severity or "").strip().lower()
    if value in {"critical", "emergency", "major"}:
        return 6
    if value in {"high", "error"}:
        return 5
    if value in {"warning", "medium"}:
        return 4
    if value in {"low", "notice", "info", "informational"}:
        return 3
    return 3
