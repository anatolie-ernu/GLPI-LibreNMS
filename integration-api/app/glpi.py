from __future__ import annotations

import asyncio
import html
from typing import Any

import httpx

from .core import severity_to_glpi_priority
from .models import LibreNmsEvent


class GLPIClient:
    """GLPI legacy REST API v1 client used for stable ITSM write operations."""

    def __init__(
        self,
        base_url: str,
        app_token: str,
        user_token: str,
        verify_tls: bool = True,
        asset_itemtype: str = "Computer",
        default_group_id: int | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.asset_itemtype = asset_itemtype
        self.default_group_id = default_group_id
        self.session_token: str | None = None
        self._session_lock = asyncio.Lock()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            verify=verify_tls,
            timeout=httpx.Timeout(20.0),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def close(self) -> None:
        if self.session_token:
            try:
                await self._request("GET", "/apirest.php/killSession/", retry_auth=False)
            except Exception:
                pass
        await self.client.aclose()

    async def _ensure_session(self, force: bool = False) -> str:
        async with self._session_lock:
            if self.session_token and not force:
                return self.session_token
            response = await self.client.get(
                "/apirest.php/initSession/",
                headers={
                    "App-Token": self.app_token,
                    "Authorization": f"user_token {self.user_token}",
                },
            )
            response.raise_for_status()
            token = response.json().get("session_token")
            if not token:
                raise RuntimeError("GLPI initSession did not return session_token")
            self.session_token = token
            return token

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        retry_auth: bool = True,
    ) -> httpx.Response:
        token = await self._ensure_session()
        response = await self.client.request(
            method,
            path,
            json=json,
            params=params,
            headers={"App-Token": self.app_token, "Session-Token": token},
        )
        if response.status_code == 401 and retry_auth:
            await self._ensure_session(force=True)
            return await self._request(
                method, path, json=json, params=params, retry_auth=False
            )
        response.raise_for_status()
        return response

    async def reachable(self) -> bool:
        try:
            response = await self._request("GET", "/apirest.php/getActiveProfile/")
            return response.status_code == 200
        except Exception:
            return False

    async def get_asset_macs(self, asset_id: int) -> list[str]:
        response = await self._request(
            "GET",
            f"/apirest.php/{self.asset_itemtype}/{int(asset_id)}/NetworkPort",
            params={"range": "0-999", "get_hateoas": "false"},
        )
        payload = response.json()
        rows = payload if isinstance(payload, list) else []
        values: list[str] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            mac = row.get("mac")
            if isinstance(mac, str) and mac.strip():
                values.append(mac.strip())
        return values

    def _ticket_content(self, event: LibreNmsEvent, key: str) -> str:
        lines = [
            "<h3>LibreNMS automated incident</h3>",
            f"<p><strong>Correlation:</strong> {html.escape(key)}</p>",
            f"<p><strong>Alert ID:</strong> {event.alert_id}</p>",
            f"<p><strong>Rule ID:</strong> {event.rule_id}</p>",
            f"<p><strong>Device:</strong> {html.escape(event.hostname)} (ID {event.device_id})</p>",
            f"<p><strong>Severity:</strong> {html.escape(event.severity or 'unknown')}</p>",
        ]
        if event.fault_object:
            lines.append(
                f"<p><strong>Fault object:</strong> {html.escape(event.fault_object)}</p>"
            )
        if event.message:
            lines.append(f"<p><strong>Message:</strong> {html.escape(event.message)}</p>")
        return "\n".join(lines)

    async def create_incident(self, event: LibreNmsEvent, key: str) -> int:
        input_data: dict[str, Any] = {
            "name": f"[LibreNMS] {event.hostname}: {event.message or event.fault_object or 'alert'}"[:250],
            "content": self._ticket_content(event, key),
            "type": 1,
            "priority": severity_to_glpi_priority(event.severity),
        }
        if self.default_group_id is not None:
            input_data["_groups_id_assign"] = self.default_group_id

        response = await self._request(
            "POST", "/apirest.php/Ticket/", json={"input": input_data}
        )
        payload = response.json()
        ticket_id = payload.get("id") if isinstance(payload, dict) else None
        if ticket_id is None:
            raise RuntimeError(f"GLPI Ticket creation returned unexpected payload: {payload!r}")
        return int(ticket_id)

    async def add_followup(self, ticket_id: int, content: str) -> int | None:
        response = await self._request(
            "POST",
            "/apirest.php/ITILFollowup/",
            json={
                "input": {
                    "itemtype": "Ticket",
                    "items_id": int(ticket_id),
                    "content": content,
                }
            },
        )
        payload = response.json()
        if isinstance(payload, dict) and payload.get("id") is not None:
            return int(payload["id"])
        return None
