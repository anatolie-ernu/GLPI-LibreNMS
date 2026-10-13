import pytest

from app.db import CorrelationStore
from app.models import EndpointResolution, LibreNmsEvent
from app.service import IntegrationService


class FakeLibreNMS:
    async def resolve_by_mac(self, mac, ip=None):
        return EndpointResolution(mac="00:11:22:33:44:55", ip=ip, confidence="high")

    async def resolve_by_ip(self, ip):
        return EndpointResolution(mac="00:11:22:33:44:55", ip=ip, confidence="high")

    async def reachable(self):
        return True


class FakeGLPI:
    def __init__(self):
        self.created = 0
        self.followups = 0

    async def get_asset_macs(self, asset_id):
        return ["00:11:22:33:44:55"]

    async def create_incident(self, event, key):
        self.created += 1
        return 1234

    async def add_followup(self, ticket_id, content):
        self.followups += 1
        return 88

    async def reachable(self):
        return True


@pytest.mark.asyncio
async def test_alert_dedup_and_recovery(tmp_path):
    store = CorrelationStore(str(tmp_path / "c.db"))
    store.initialize()
    glpi = FakeGLPI()
    svc = IntegrationService(store, FakeLibreNMS(), glpi)

    alert = LibreNmsEvent(
        alert_id=1,
        rule_id=2,
        device_id=3,
        hostname="switch01",
        severity="critical",
        state="alert",
        fault_object="device",
    )
    created = await svc.handle_event(alert)
    assert created.action == "created"
    assert created.glpi_ticket_id == 1234
    assert glpi.created == 1

    duplicate = await svc.handle_event(alert)
    assert duplicate.action == "ignored"
    assert glpi.created == 1

    recovery = alert.model_copy(update={"state": "recovered"})
    recovered = await svc.handle_event(recovery)
    assert recovered.action == "recovered"
    assert glpi.followups == 1

    repeated_recovery = await svc.handle_event(recovery)
    assert repeated_recovery.action == "ignored"
    assert glpi.followups == 1
