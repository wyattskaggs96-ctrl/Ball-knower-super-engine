from __future__ import annotations

from app.core.models import TrendCandidate


def fetch_trends() -> list[TrendCandidate]:
    # Placeholder for future integration.
    return [
        TrendCandidate(
            source="twitter",
            topic="Woj-style rumor cycle intensifies",
            summary="Mock trend reserved for future source expansion.",
            sport="basketball",
        )
    ]
