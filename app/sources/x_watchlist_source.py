from __future__ import annotations

import json
from pathlib import Path

from app.sources.trend_item import NormalizedTrendItem
from app.sources.trend_normalizer import normalize_trend_item

DEFAULT_X_WATCHLIST_PATH = Path(__file__).resolve().parents[2] / "data" / "x_watchlist.json"


def fetch_trends(data_path: str | None = None) -> list[NormalizedTrendItem]:
    source_path = Path(data_path) if data_path else DEFAULT_X_WATCHLIST_PATH
    if not source_path.exists():
        return []

    rows = json.loads(source_path.read_text(encoding="utf-8"))
    items: list[NormalizedTrendItem] = []
    for row in rows:
        title = row.get("topic", "X watchlist topic")
        summary = row.get("summary", "Manual X watchlist entry")
        tags = row.get("tags", [])
        items.append(
            normalize_trend_item(
                source="x_watchlist",
                source_type="manual_watchlist",
                title=title,
                url=row.get("url"),
                summary=summary,
                team_tags=tags,
                topic_type=row.get("topic_type"),
                urgency=row.get("urgency"),
            )
        )
    return items
