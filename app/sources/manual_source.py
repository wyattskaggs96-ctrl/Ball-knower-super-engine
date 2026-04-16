from __future__ import annotations

from app.core.models import TrendCandidate


def fetch_trends(topics: list[str] | None = None) -> list[TrendCandidate]:
    topics = topics or ["Is this the year an underdog wins the title?"]
    return [
        TrendCandidate(
            source="manual",
            topic=t,
            summary="Manual entry from creator/editor shortlist.",
            sport="general",
        )
        for t in topics
    ]
