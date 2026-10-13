from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from .core import display_mac, normalize_ip, normalize_mac
from .models import DeviceRef, EndpointResolution, PortRef


class LibreNMSClient:
    def __init__(self, base_url: str, token: str, verify_tls: bool = True):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            verify=verify_tls,
            timeout=httpx.Timeout(15.0),
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and payload.get("status") == "error":
            raise RuntimeError(payload.get("message") or f"LibreNMS error for {path}")
        return payload

    async def reachable(self) -> bool:
        try:
            await self._get("/api/v0")
            return True
        except Exception:
            return False

    async def arp_by_ip(self, ip: str) -> list[dict[str, Any]]:
        value = normalize_ip(ip)
        payload = await self._get(f"/api/v0/resources/ip/arp/{value}")
        return list(payload.get("arp") or [])

    async def fdb_by_mac(self, mac: str) -> list[dict[str, Any]]:
        value = normalize_mac(mac)
        payload = await self._get(f"/api/v0/resources/fdb/{value}")
        return list(payload.get("ports_fdb") or [])

    async def port_info(self, port_id: int) -> dict[str, Any] | None:
        payload = await self._get(
            f"/api/v0/ports/{int(port_id)}", params={"with": "device,vlans"}
        )
        port = payload.get("port")
        if isinstance(port, list):
            return port[0] if port else None
        return port if isinstance(port, dict) else None

    async def device_info(self, device_id: int) -> dict[str, Any] | None:
        payload = await self._get(f"/api/v0/devices/{int(device_id)}")
        devices = payload.get("devices")
        if isinstance(devices, list):
            return devices[0] if devices else None
        return devices if isinstance(devices, dict) else None

    @staticmethod
    def _port_score(port: dict[str, Any]) -> int:
        score = 0
        if str(port.get("ifOperStatus", "")).lower() == "up":
            score += 2
        text = " ".join(
            str(port.get(key) or "").lower()
            for key in ("ifName", "ifAlias", "ifDescr", "portName")
        )
        for marker in ("port-channel", "portchannel", "po", "ae", "bond", "lag", "uplink", "trunk"):
            if marker in text:
                score -= 2
        return score

    async def resolve_by_mac(self, mac: str, ip: str | None = None) -> EndpointResolution | None:
        compact = normalize_mac(mac)
        fdb_rows = await self.fdb_by_mac(compact)
        if not fdb_rows:
            return None

        candidates: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
        for row in fdb_rows:
            port_id = row.get("port_id")
            if port_id is None:
                continue
            port = await self.port_info(int(port_id))
            if not port:
                continue
            candidates.append((self._port_score(port), row, port))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)
        score, row, port = candidates[0]

        device_id = int(row.get("device_id") or port.get("device_id") or 0) or None
        embedded = port.get("device") if isinstance(port.get("device"), dict) else None
        device = embedded
        if not device and device_id:
            device = await self.device_info(device_id)

        hostname = None
        if device:
            hostname = device.get("hostname") or device.get("sysName")
        if not hostname:
            hostname = port.get("hostname") or port.get("sysName")

        vlan_raw = row.get("vlan_id")
        try:
            vlan = int(vlan_raw) if vlan_raw not in (None, "") else None
        except (TypeError, ValueError):
            vlan = None

        last_seen = None
        for value in (row.get("updated_at"), row.get("last_seen")):
            if isinstance(value, str):
                try:
                    last_seen = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    break
                except ValueError:
                    pass

        top_score_count = sum(1 for candidate in candidates if candidate[0] == score)
        if len(candidates) == 1:
            confidence = "high"
        elif top_score_count == 1:
            confidence = "medium"
        else:
            confidence = "low"

        return EndpointResolution(
            hostname=hostname,
            ip=normalize_ip(ip) if ip else None,
            mac=display_mac(compact),
            device=DeviceRef(id=device_id, hostname=hostname),
            port=PortRef(
                id=int(port.get("port_id")) if port.get("port_id") is not None else None,
                ifName=port.get("ifName") or port.get("ifDescr"),
                status=port.get("ifOperStatus"),
                ifAlias=port.get("ifAlias"),
            ),
            vlan=vlan,
            confidence=confidence,
            last_seen=last_seen,
            evidence_sources=["librenms:api-v0:fdb", "librenms:api-v0:ports"],
        )

    async def resolve_by_ip(self, ip: str) -> EndpointResolution | None:
        value = normalize_ip(ip)
        arp_rows = await self.arp_by_ip(value)
        if not arp_rows:
            return None
        mac = arp_rows[0].get("mac_address")
        if not mac:
            return None
        result = await self.resolve_by_mac(str(mac), ip=value)
        if result:
            result.evidence_sources.insert(0, "librenms:api-v0:arp")
        return result
