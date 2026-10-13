from app.db import CorrelationStore


def test_store_lifecycle(tmp_path):
    store = CorrelationStore(str(tmp_path / "c.db"))
    store.initialize()

    assert store.get("x") is None
    created = store.create("x", 10, 20)
    assert created.state == "open"
    assert created.glpi_ticket_id == 20

    recovered = store.update_state("x", "recovered")
    assert recovered.state == "recovered"
