from __future__ import annotations

from app.agents.trend_scout import TrendScoutAgent
from app.core.config import Settings


class TrendService:
    def __init__(self, scout: TrendScoutAgent, settings: Settings) -> None:
        self.scout = scout
        self.settings = settings

    def scout_trends(self) -> list[int]:
        return self.scout.run(
            enable_rss=self.settings.enable_rss,
            enable_reddit=self.settings.enable_reddit,
            enable_manual=self.settings.enable_manual,
        )
