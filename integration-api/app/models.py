from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DeviceRef(BaseModel):
    id: int | None = None
    hostname: str | None = None


class PortRef(BaseModel):
    id: int | None = None
    ifName: str | None = None
    status: str | None = None
    ifAlias: str | None = None


class EndpointResolution(BaseModel):
    hostname: str | None = None
    ip: str | None = None
    mac: str
    device: DeviceRef | None = None
    port: PortRef | None = None
    vlan: int | None = None
    confidence: Literal["high", "medium", "low"] = "low"
    last_seen: datetime | None = None
    evidence_sources: list[str] = Field(default_factory=list)


class AssetNetworkResponse(BaseModel):
    asset_id: int
    endpoint: EndpointResolution


class LibreNmsEvent(BaseModel):
    alert_id: int
    rule_id: int
    device_id: int
    hostname: str
    severity: str | None = None
    state: str | int | bool
    timestamp: datetime | None = None
    fault_object: str | None = None
    message: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class EventAccepted(BaseModel):
    accepted: bool
    correlation_key: str
    glpi_ticket_id: int | None = None
    action: Literal["created", "updated", "recovered", "ignored"]


class Correlation(BaseModel):
    key: str
    librenms_alert_id: int
    glpi_ticket_id: int
    state: Literal["open", "recovered", "closed"]
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    librenms: Literal["reachable", "unreachable", "unknown"] = "unknown"
    glpi: Literal["reachable", "unreachable", "unknown"] = "unknown"
