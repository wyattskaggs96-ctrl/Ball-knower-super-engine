from app.core.models import TrendCandidate
from app.sources.trend_source_framework import TrendSourceDefinition, collect_trends


def test_collect_trends_dedupes_by_topic_and_tracks_source_contributions(monkeypatch):
    manual_rows = [
        TrendCandidate(source="manual", topic="NBA Finals debate", summary="manual", sport="nba"),
    ]
    live_rows = [
        TrendCandidate(source="live", topic="nba finals debate", summary="dupe", sport="nba"),
        TrendCandidate(source="live", topic="Lakers playoff rotation questions", summary="new", sport="nba"),
    ]

    monkeypatch.setenv("ENABLE_LIVE_TRENDS", "true")

    sources = [
        TrendSourceDefinition("manual_curated", "manual", 1, lambda: manual_rows),
        TrendSourceDefinition("newsapi_live", "news", 2, lambda: live_rows, enabled_env_var="ENABLE_LIVE_TRENDS"),
    ]

    trends, report = collect_trends(sources)

    assert len(trends) == 2
    assert report["manual_curated"]["ingested"] == 1
    assert report["newsapi_live"]["fetched"] == 2
    assert report["newsapi_live"]["ingested"] == 1
    assert trends[0].source_name == "manual_curated"
    assert trends[1].source_name == "newsapi_live"
