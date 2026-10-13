from __future__ import annotations

import asyncio
from typing import Protocol

from .core import correlation_key, is_recovery_state
from .db import CorrelationStore
from .models import (
    AssetNetworkResponse,
    Correlation,
    EndpointResolution,
    EventAccepted,
    LibreNmsEvent,
)


class LibreNMSProtocol(Protocol):
    async def resolve_by_mac(self, mac: str, ip: str | None = None) -> EndpointResolution | None: ...
    async def resolve_by_ip(self, ip: str) -> EndpointResolution | None: ...
    async def reachable(self) -> bool: ...


class GLPIProtocol(Protocol):
    async def get_asset_macs(self, asset_id: int) -> list[str]: ...
    async def create_incident(self, event: LibreNmsEvent, key: str) -> int: ...
    async def add_followup(self, ticket_id: int, content: str) -> int | None: ...
    async def reachable(self) -> bool: ...


class IntegrationService:
    def __init__(
        self,
        store: CorrelationStore,
        librenms: LibreNMSProtocol,
        glpi: GLPIProtocol,
    ):
        self.store = store
        self.librenms = librenms
        self.glpi = glpi
        self._event_lock = asyncio.Lock()

    async def endpoint_by_mac(self, mac: str) -> EndpointResolution | None:
        return await self.librenms.resolve_by_mac(mac)

    async def endpoint_by_ip(self, ip: str) -> EndpointResolution | None:
        return await self.librenms.resolve_by_ip(ip)

    async def asset_network(self, asset_id: int) -> AssetNetworkResponse | None:
        macs = await self.glpi.get_asset_macs(asset_id)
        for mac in macs:
            endpoint = await self.librenms.resolve_by_mac(mac)
            if endpoint:
                return AssetNetworkResponse(asset_id=asset_id, endpoint=endpoint)
        return None

    def get_correlation(self, key: str) -> Correlation | None:
        return self.store.get(key)

    async def handle_event(self, event: LibreNmsEvent) -> EventAccepted:
        key = correlation_key(event)
        recovery = is_recovery_state(event.state)

        async with self._event_lock:
            current = self.store.get(key)

            if current:
                if recovery:
                    if current.state == "recovered":
                        return EventAccepted(
                            accepted=True,
                            correlation_key=key,
                            glpi_ticket_id=current.glpi_ticket_id,
                            action="ignored",
                        )
                    await self.glpi.add_followup(
                        current.glpi_ticket_id,
                        (
                            "LibreNMS recovery received. "
                            f"Alert ID={event.alert_id}; state={event.state}; "
                            f"message={event.message or ''}"
                        ),
                    )
                    updated = self.store.update_state(key, "recovered")
                    return EventAccepted(
                        accepted=True,
                        correlation_key=key,
                        glpi_ticket_id=updated.glpi_ticket_id,
                        action="recovered",
                    )

                return EventAccepted(
                    accepted=True,
                    correlation_key=key,
                    glpi_ticket_id=current.glpi_ticket_id,
                    action="ignored",
                )

            if recovery:
                return EventAccepted(
                    accepted=True,
                    correlation_key=key,
                    glpi_ticket_id=None,
                    action="ignored",
                )

            ticket_id = await self.glpi.create_incident(event, key)
            self.store.create(key, event.alert_id, ticket_id, "open")
            return EventAccepted(
                accepted=True,
                correlation_key=key,
                glpi_ticket_id=ticket_id,
                action="created",
            )
