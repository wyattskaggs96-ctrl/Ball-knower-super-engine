from app.agents.trend_scout import TrendScoutAgent
from app.core.models import TrendCandidate


class DummyRepo:
    def insert_trend_candidates(self, trends):
        return [1]


def test_dedupe():
    agent = TrendScoutAgent(DummyRepo())
    items = [
        TrendCandidate(source="rss", topic="NBA Finals debate", summary="a", fingerprint="x"),
        TrendCandidate(source="reddit", topic="nba finals debate", summary="b", fingerprint="x"),
    ]
    out = agent.dedupe(items)
    assert len(out) == 1
