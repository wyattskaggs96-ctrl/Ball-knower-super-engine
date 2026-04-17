from pathlib import Path

from app.pipelines.trend_source_ingestion import build_report_payload, collect_source_items, dedupe_items
from app.sources.trend_item import NormalizedTrendItem
from app.sources.x_watchlist_source import fetch_trends


def test_normalized_trend_item_structure():
    item = NormalizedTrendItem(
        source="espn",
        source_type="public_feed",
        title="Breaking trade update",
        url="https://example.com/trade",
        summary="A major trade is developing.",
        team_tags=["Lakers"],
        player_tags=["LeBron James"],
        topic_type="breaking_news",
        urgency="high",
        trend_weight=1.9,
    )

    data = item.model_dump()
    expected_fields = {
        "source",
        "source_type",
        "title",
        "url",
        "summary",
        "team_tags",
        "player_tags",
        "topic_type",
        "urgency",
        "trend_weight",
        "collected_at",
    }
    assert expected_fields.issubset(set(data.keys()))


def test_x_watchlist_ingestion(tmp_path: Path):
    watchlist = tmp_path / "x_watchlist.json"
    watchlist.write_text(
        '[{"topic":"Portal watch update","source_account":"@test","url":"https://x.com/test/1","summary":"Monitor portal","urgency":"high","tags":["portal"]}]',
        encoding="utf-8",
    )

    items = fetch_trends(str(watchlist))

    assert len(items) == 1
    assert items[0].source == "x_watchlist"
    assert items[0].source_type == "manual_watchlist"
    assert items[0].urgency == "high"


def test_aggregation_deduplication_behavior():
    items = [
        NormalizedTrendItem(source="espn", source_type="public_feed", title="NBA Finals injury watch for stars"),
        NormalizedTrendItem(source="bleacher_report", source_type="public_feed", title="NBA Finals injury watch for stars"),
        NormalizedTrendItem(source="on3", source_type="public_feed", title="Recruiting commitment update from five-star QB", topic_type="recruiting"),
    ]

    deduped = dedupe_items(items)
    payload = build_report_payload(deduped)

    assert len(deduped) == 2
    assert payload["totals"]["items"] == 2
    assert "top_trends_by_source" in payload


def test_collect_source_items_covers_all_v1_sources():
    items, source_counts = collect_source_items()

    assert len(items) >= 4
    assert source_counts["espn"] >= 1
    assert source_counts["bleacher_report"] >= 1
    assert source_counts["on3"] >= 1
    assert source_counts["x_watchlist"] >= 1
