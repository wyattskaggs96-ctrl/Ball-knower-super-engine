from __future__ import annotations

from app.core.models import TrendCandidate


def fetch_trends() -> list[TrendCandidate]:
    # Mock Reddit adapter output for V1.
    return [
        TrendCandidate(
            source="reddit",
            topic="Should contenders trade for a veteran rim protector?",
            summary="Fans debate if a late-season defensive move can swing playoffs.",
            url="https://reddit.com/r/nba/example",
            sport="basketball",
        ),
        TrendCandidate(
            source="reddit",
            topic="MLB manager ejection clip goes viral",
            summary="A heated dugout argument is getting meme-level traction.",
            url="https://reddit.com/r/baseball/example",
            sport="baseball",
        ),
    ]
