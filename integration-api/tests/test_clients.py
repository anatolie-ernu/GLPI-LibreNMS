import json

import httpx
import pytest

from app.glpi import GLPIClient
from app.librenms import LibreNMSClient
from app.models import LibreNmsEvent


@pytest.mark.asyncio
async def test_librenms_ip_to_switch_port_contract():
    async def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/v0/resources/ip/arp/10.0.0.25":
            return httpx.Response(
                200,
                json={
                    "status": "ok",
                    "arp": [
                        {
                            "port_id": "1",
                            "mac_address": "001122334455",
                            "ipv4_address": "10.0.0.25",
                        }
                    ],
                },
            )
        if path == "/api/v0/resources/fdb/001122334455":
            return httpx.Response(
                200,
                json={
                    "status": "ok",
                    "ports_fdb": [
                        {
                            "port_id": "100",
                            "device_id": "42",
                            "vlan_id": "129",
                            "mac_address": "001122334455",
                        }
                    ],
                },
            )
        if path == "/api/v0/ports/100":
            return httpx.Response(
                200,
                json={
                    "status": "ok",
                    "port": [
                        {
                            "port_id": "100",
                            "device_id": "42",
                            "ifName": "Gi1/0/31",
                            "ifAlias": "User port",
                            "ifOperStatus": "up",
                        }
                    ],
                },
            )
        if path == "/api/v0/devices/42":
            return httpx.Response(
                200,
                json={
                    "status": "ok",
                    "devices": [{"device_id": "42", "hostname": "HQ-ACCESS-SW-04"}],
                },
            )
        return httpx.Response(404, json={"status": "error", "message": path})

    client = LibreNMSClient("https://librenms.test", "token")
    await client.client.aclose()
    client.client = httpx.AsyncClient(
        base_url="https://librenms.test",
        transport=httpx.MockTransport(handler),
        headers={"Authorization": "Bearer token"},
    )
    try:
        result = await client.resolve_by_ip("10.0.0.25")
    finally:
        await client.close()

    assert result is not None
    assert result.ip == "10.0.0.25"
    assert result.mac == "00:11:22:33:44:55"
    assert result.device.hostname == "HQ-ACCESS-SW-04"
    assert result.port.ifName == "Gi1/0/31"
    assert result.vlan == 129
    assert result.confidence == "high"


@pytest.mark.asyncio
async def test_glpi_create_ticket_and_recovery_followup_contract():
    calls: list[tuple[str, str]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        calls.append((request.method, path))

        if path == "/apirest.php/initSession/":
            assert request.headers.get("App-Token") == "app-token"
            assert request.headers.get("Authorization") == "user_token user-token"
            return httpx.Response(200, json={"session_token": "session-token"})

        assert request.headers.get("App-Token") == "app-token"
        assert request.headers.get("Session-Token") == "session-token"

        if path == "/apirest.php/Ticket/" and request.method == "POST":
            payload = json.loads(request.content)
            assert payload["input"]["type"] == 1
            assert payload["input"]["priority"] == 6
            assert payload["input"]["_groups_id_assign"] == 12
            return httpx.Response(201, json={"id": 456})

        if path == "/apirest.php/ITILFollowup/" and request.method == "POST":
            payload = json.loads(request.content)
            assert payload["input"]["itemtype"] == "Ticket"
            assert payload["input"]["items_id"] == 456
            return httpx.Response(201, json={"id": 789})

        if path == "/apirest.php/killSession/":
            return httpx.Response(200, json={})

        return httpx.Response(404, json={"error": path})

    client = GLPIClient(
        "https://glpi.test",
        app_token="app-token",
        user_token="user-token",
        default_group_id=12,
    )
    await client.client.aclose()
    client.client = httpx.AsyncClient(
        base_url="https://glpi.test",
        transport=httpx.MockTransport(handler),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )

    event = LibreNmsEvent(
        alert_id=1,
        rule_id=2,
        device_id=3,
        hostname="sw-core-01",
        severity="critical",
        state="alert",
        fault_object="device",
        message="Device down",
    )

    ticket_id = await client.create_incident(event, "librenms:3:2:device")
    assert ticket_id == 456
    followup_id = await client.add_followup(ticket_id, "Recovered")
    assert followup_id == 789
    await client.close()

    assert ("POST", "/apirest.php/Ticket/") in calls
    assert ("POST", "/apirest.php/ITILFollowup/") in calls
