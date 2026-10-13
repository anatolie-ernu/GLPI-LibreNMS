from app.core import (
    correlation_key,
    display_mac,
    is_recovery_state,
    normalize_ip,
    normalize_mac,
    severity_to_glpi_priority,
)
from app.models import LibreNmsEvent


def test_normalize_mac():
    assert normalize_mac("00:25:90:AB:CD:EF") == "002590abcdef"
    assert display_mac("002590ABCDEF") == "00:25:90:ab:cd:ef"


def test_normalize_ip():
    assert normalize_ip("10.0.0.1") == "10.0.0.1"


def test_correlation_key():
    event = LibreNmsEvent(
        alert_id=99,
        rule_id=7,
        device_id=42,
        hostname="sw1",
        state="alert",
        fault_object="port:Gi1/0/1",
    )
    assert correlation_key(event) == "librenms:42:7:port_Gi1/0/1"


def test_recovery_states():
    assert is_recovery_state("recovered")
    assert is_recovery_state(0)
    assert is_recovery_state(False)
    assert not is_recovery_state("alert")
    assert not is_recovery_state(1)


def test_severity_mapping():
    assert severity_to_glpi_priority("critical") == 6
    assert severity_to_glpi_priority("high") == 5
    assert severity_to_glpi_priority("warning") == 4
    assert severity_to_glpi_priority("info") == 3
