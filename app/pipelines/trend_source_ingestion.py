from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from app.sources import bleacher_report_source, espn_source, on3_source, x_watchlist_source
from app.sources.trend_item import NormalizedTrendItem
from app.sources.trend_normalizer import title_fingerprint

DEFAULT_EXPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "exports"


def collect_source_items(x_watchlist_path: str | None = None) -> tuple[list[NormalizedTrendItem], dict[str, int]]:
    by_source = {
        "espn": espn_source.fetch_trends(),
        "bleacher_report": bleacher_report_source.fetch_trends(),
        "on3": on3_source.fetch_trends(),
        "x_watchlist": x_watchlist_source.fetch_trends(data_path=x_watchlist_path),
    }
    items: list[NormalizedTrendItem] = []
    for rows in by_source.values():
        items.extend(rows)
    source_counts = {source: len(rows) for source, rows in by_source.items()}
    return items, source_counts


def dedupe_items(items: list[NormalizedTrendItem]) -> list[NormalizedTrendItem]:
    deduped: list[NormalizedTrendItem] = []
    fingerprints: list[set[str]] = []

    for item in items:
        current_tokens = set(title_fingerprint(item.title).split())
        if not current_tokens:
            deduped.append(item)
            continue

        duplicate = False
        for seen_tokens in fingerprints:
            overlap = len(current_tokens & seen_tokens) / max(len(current_tokens), 1)
            if overlap >= 0.8:
                duplicate = True
                break
        if duplicate:
            continue

        deduped.append(item)
        fingerprints.append(current_tokens)

    return deduped


def build_report_payload(items: list[NormalizedTrendItem], source_counts: dict[str, int] | None = None) -> dict:
    sorted_items = sorted(items, key=lambda x: (x.trend_weight, x.urgency == "high"), reverse=True)

    by_source: dict[str, list[dict]] = defaultdict(list)
    for item in sorted_items:
        by_source[item.source].append(item.model_dump(mode="json"))

    repeated_themes = [
        {"topic_type": topic_type, "count": count}
        for topic_type, count in Counter(item.topic_type for item in items).most_common()
        if count > 1
    ]

    high_urgency_items = [item.model_dump(mode="json") for item in items if item.urgency == "high"]
    recruiting_or_portal = [
        item.model_dump(mode="json")
        for item in items
        if item.topic_type in {"recruiting", "transfer_portal"}
    ]
    broad_reach = [
        item.model_dump(mode="json")
        for item in sorted_items
        if item.topic_type in {"championship", "breaking_news", "general"}
    ]

    return {
        "totals": {"items": len(items), "sources": len(by_source)},
        "source_item_counts": source_counts or {},
        "top_trends_by_source": {source: rows[:5] for source, rows in by_source.items()},
        "repeated_themes": repeated_themes,
        "high_urgency_items": high_urgency_items,
        "likely_recruiting_or_portal_moves": recruiting_or_portal,
        "likely_broad_reach_sports_moments": broad_reach[:10],
    }


def _format_markdown_report(payload: dict) -> str:
    lines = [
        "# Trend Source Report",
        "",
        f"- Total trend items: {payload['totals']['items']}",
        f"- Sources covered: {payload['totals']['sources']}",
        "",
        "## Source item counts",
        f"- ESPN: {payload['source_item_counts'].get('espn', 0)}",
        f"- Bleacher Report: {payload['source_item_counts'].get('bleacher_report', 0)}",
        f"- On3: {payload['source_item_counts'].get('on3', 0)}",
        f"- X watchlist: {payload['source_item_counts'].get('x_watchlist', 0)}",
        "",
        "## Top trend items by source",
    ]

    for source, rows in payload["top_trends_by_source"].items():
        lines.append(f"### {source}")
        for row in rows:
            lines.append(f"- **{row['title']}** ({row['topic_type']}, urgency: {row['urgency']})")
        lines.append("")

    lines.append("## Repeated themes across sources")
    for theme in payload["repeated_themes"]:
        lines.append(f"- {theme['topic_type']}: {theme['count']} items")
    lines.append("")

    lines.append("## High-urgency items")
    for row in payload["high_urgency_items"][:10]:
        lines.append(f"- {row['title']} ({row['source']})")
    lines.append("")

    lines.append("## Likely recruiting/portal moves")
    for row in payload["likely_recruiting_or_portal_moves"][:10]:
        lines.append(f"- {row['title']} ({row['source']})")
    lines.append("")

    lines.append("## Likely broad-reach sports moments")
    for row in payload["likely_broad_reach_sports_moments"][:10]:
        lines.append(f"- {row['title']} ({row['source']})")

    return "\n".join(lines) + "\n"


def export_trend_source_report(
    items: list[NormalizedTrendItem],
    export_dir: str | Path = DEFAULT_EXPORT_DIR,
    source_counts: dict[str, int] | None = None,
) -> tuple[Path, Path]:
    output_dir = Path(export_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = build_report_payload(items, source_counts=source_counts)

    json_path = output_dir / "trend_source_report.json"
    md_path = output_dir / "trend_source_report.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_format_markdown_report(payload), encoding="utf-8")

    return md_path, json_path


def run_trend_source_ingestion(x_watchlist_path: str | None = None) -> tuple[Path, Path]:
    items, source_counts = collect_source_items(x_watchlist_path=x_watchlist_path)
    deduped = dedupe_items(items)
    return export_trend_source_report(deduped, source_counts=source_counts)
