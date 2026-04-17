from __future__ import annotations

import json
from pathlib import Path

from app.sources.private_intel_source import load_private_intel, normalize_private_intel_items

DEFAULT_EXPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "exports"


def build_private_intel_report_payload(data_path: str | Path | None = None) -> dict:
    raw_items = load_private_intel(data_path) if data_path else load_private_intel()
    normalized_items = normalize_private_intel_items(raw_items)

    raw_json = [item.model_dump(mode="json") for item in raw_items]
    normalized_json = [item.model_dump(mode="json") for item in normalized_items]

    highest_urgency = [row for row in normalized_json if row["urgency"] == "high"]
    highest_confidence = sorted(raw_json, key=lambda row: _confidence_score(row["confidence"]), reverse=True)
    likely_recruiting_or_portal_moves = [
        row for row in normalized_json if row["topic_type"] in {"recruiting", "transfer_portal"}
    ]
    likely_early_story_opportunities = [
        row
        for row in sorted(normalized_json, key=lambda item: item["trend_weight"], reverse=True)
        if row["topic_type"] in {"recruiting", "transfer_portal", "rumor", "breaking_news"}
    ]

    return {
        "totals": {"items": len(raw_json)},
        "all_private_intel_items": raw_json,
        "normalized_trend_items": normalized_json,
        "highest_urgency_items": highest_urgency,
        "highest_confidence_items": highest_confidence,
        "likely_recruiting_or_portal_moves": likely_recruiting_or_portal_moves,
        "likely_stories_to_post_before_mainstream": likely_early_story_opportunities[:10],
    }


def _confidence_score(value: str | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return {"high": 0.9, "medium": 0.7, "low": 0.4}.get(value, 0.0)


def _format_markdown_report(payload: dict) -> str:
    lines = [
        "# Private Intel Report",
        "",
        f"- Total private intel items: {payload['totals']['items']}",
        "",
        "## All private intel items",
    ]

    for row in payload["all_private_intel_items"]:
        lines.append(
            f"- **{row['title']}** | type: {row['note_type']} | urgency: {row['urgency']} | confidence: {row['confidence']}"
        )
    lines.append("")

    lines.append("## Highest urgency items")
    for row in payload["highest_urgency_items"]:
        lines.append(f"- {row['title']} ({row['source']})")
    lines.append("")

    lines.append("## Highest confidence items")
    for row in payload["highest_confidence_items"][:10]:
        lines.append(f"- {row['title']} ({row['source']}, confidence: {row['confidence']})")
    lines.append("")

    lines.append("## Likely recruiting/portal moves")
    for row in payload["likely_recruiting_or_portal_moves"][:10]:
        lines.append(f"- {row['title']} ({row['source']})")
    lines.append("")

    lines.append("## Likely stories worth posting before they go mainstream")
    for row in payload["likely_stories_to_post_before_mainstream"]:
        lines.append(f"- {row['title']} ({row['source']}, trend_weight: {row['trend_weight']})")

    return "\n".join(lines) + "\n"


def export_private_intel_report(
    export_dir: str | Path = DEFAULT_EXPORT_DIR,
    data_path: str | Path | None = None,
) -> tuple[Path, Path]:
    output_dir = Path(export_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = build_private_intel_report_payload(data_path=data_path)

    json_path = output_dir / "private_intel_report.json"
    md_path = output_dir / "private_intel_report.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_format_markdown_report(payload), encoding="utf-8")

    return md_path, json_path
