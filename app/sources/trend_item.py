from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class NormalizedTrendItem(BaseModel):
    source: str
    source_type: str
    title: str
    url: str | None = None
    summary: str = ""
    team_tags: list[str] = Field(default_factory=list)
    player_tags: list[str] = Field(default_factory=list)
    topic_type: str = "general"
    urgency: str = "medium"
    trend_weight: float = 1.0
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
