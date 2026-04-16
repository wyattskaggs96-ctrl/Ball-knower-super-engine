from __future__ import annotations

from app.core.models import TrendCandidate


def fetch_trends() -> list[TrendCandidate]:
    # Mock feed data for V1. Replace with real RSS parser later.
    return [
        TrendCandidate(
            source="rss",
            topic="NBA Finals rotation debate is heating up",
            summary="Analysts are split over bench usage in the NBA Finals.",
            url="https://example.com/nba-finals-rotation",
            sport="basketball",
        ),
        TrendCandidate(
            source="rss",
            topic="NFL preseason QB battle sparks early drama",
            summary="Two quarterbacks are in a tight race for starter reps.",
            url="https://example.com/nfl-qb-battle",
            sport="football",
        ),
    ]
