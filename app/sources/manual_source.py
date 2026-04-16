from __future__ import annotations

import json
from pathlib import Path

from app.core.models import TrendCandidate


DEFAULT_SAMPLE_TRENDS_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_trends.json"


def _load_from_json(path: Path) -> list[TrendCandidate]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    trends: list[TrendCandidate] = []
    for row in rows:
        trends.append(
            TrendCandidate(
                source=row.get("source", "manual"),
                topic=row["topic"],
                summary=row.get("summary", "Manual entry from creator/editor shortlist."),
                sport=row.get("sport", "general"),
                url=row.get("url"),
            )
        )
    return trends


def fetch_trends(topics: list[str] | None = None, data_path: str | None = None) -> list[TrendCandidate]:
    if topics:
        return [
            TrendCandidate(
                source="manual",
                topic=t,
                summary="Manual entry from creator/editor shortlist.",
                sport="general",
            )
            for t in topics
        ]

    source_path = Path(data_path) if data_path else DEFAULT_SAMPLE_TRENDS_PATH
    if source_path.exists():
        return _load_from_json(source_path)

    return [
        TrendCandidate(
            source="manual",
            topic="Is this the year an underdog wins the title?",
            summary="Fallback manual trend when sample file is unavailable.",
            sport="general",
        )
    ]
