from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Correlation


class CorrelationStore:
    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        db_path = Path(self.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS correlations (
                    correlation_key TEXT PRIMARY KEY,
                    librenms_alert_id INTEGER NOT NULL,
                    glpi_ticket_id INTEGER NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('open','recovered','closed')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_correlations_alert_id "
                "ON correlations(librenms_alert_id)"
            )
            conn.commit()

    def get(self, key: str) -> Correlation | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM correlations WHERE correlation_key = ?", (key,)
            ).fetchone()
        if not row:
            return None
        return Correlation(
            key=row["correlation_key"],
            librenms_alert_id=row["librenms_alert_id"],
            glpi_ticket_id=row["glpi_ticket_id"],
            state=row["state"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create(
        self, key: str, alert_id: int, ticket_id: int, state: str = "open"
    ) -> Correlation:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO correlations (
                    correlation_key, librenms_alert_id, glpi_ticket_id,
                    state, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (key, alert_id, ticket_id, state, now, now),
            )
            conn.commit()
        item = self.get(key)
        assert item is not None
        return item

    def update_state(self, key: str, state: str) -> Correlation:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute(
                "UPDATE correlations SET state = ?, updated_at = ? "
                "WHERE correlation_key = ?",
                (state, now, key),
            )
            if cursor.rowcount != 1:
                raise KeyError(key)
            conn.commit()
        item = self.get(key)
        assert item is not None
        return item
