from __future__ import annotations

import sqlite3

from app.core.utils import utc_now_iso


class PerformanceLoggerAgent:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def log_metric(self, content_pack_id: int, platform: str, metric_name: str, metric_value: float) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO performance_logs (content_pack_id, platform, metric_name, metric_value, logged_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (content_pack_id, platform, metric_name, metric_value, utc_now_iso()),
        )
        self.conn.commit()
        return cur.lastrowid
