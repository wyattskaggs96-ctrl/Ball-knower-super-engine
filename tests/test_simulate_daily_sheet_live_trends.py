import json

from app.core.models import TrendCandidate
from app.pipelines import simulate_daily_sheet


def test_simulate_daily_content_sheet_merges_and_dedupes_live_trends(monkeypatch, tmp_path):
    manual_trends = [
        TrendCandidate(source="manual", topic="NBA Finals debate", summary="manual", sport="nba"),
    ]
    live_trends = [
        TrendCandidate(source="live", topic="nba finals debate", summary="duplicate", sport="nba"),
        TrendCandidate(source="live", topic="Celtics trade rumor heats up", summary="unique", sport="nba"),
    ]

    monkeypatch.setattr(simulate_daily_sheet.manual_source, "fetch_trends", lambda: manual_trends)
    monkeypatch.setattr(simulate_daily_sheet, "fetch_live_trends", lambda: live_trends)
    monkeypatch.setenv("ENABLE_LIVE_TRENDS", "true")

    output_path = tmp_path / "daily_content_sheet.md"
    result = simulate_daily_sheet.simulate_daily_content_sheet(str(output_path))

    assert result["manual_trends_count"] == 1
    assert result["live_trends_fetched"] == 2
    assert result["live_trends_ingested"] == 1
    assert result["total_trends_considered"] == 2

    rows = json.loads((tmp_path / "daily_content_sheet.json").read_text(encoding="utf-8"))
    topics = {row["topic"].lower() for row in rows}
    assert "nba finals debate" in topics
    assert "celtics trade rumor heats up" in topics
