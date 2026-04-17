from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.pipelines.simulate_daily_sheet import simulate_daily_content_sheet


def _extract_hashtags(caption: str) -> str:
    tags = re.findall(r"#[A-Za-z0-9_]+", caption)
    return " ".join(tags)


def _best_window(engine_recommendations_path: Path) -> str:
    if not engine_recommendations_path.exists():
        return "late_night"

    payload = json.loads(engine_recommendations_path.read_text(encoding="utf-8"))
    for rec in payload.get("recommendations", []):
        if rec.get("engine_target") == "posting recommendations" and rec.get("action") == "increase":
            return str(rec.get("focus", "late_night"))

    return "late_night"


def _card_for_goal(
    rows: list[dict],
    goal: str,
    weighted_metric_key: str,
    fallback_metric_key: str,
    best_window: str,
) -> dict:
    def score_for_row(row: dict) -> float:
        if weighted_metric_key in row:
            return row.get(weighted_metric_key, 0.0)
        return row.get(fallback_metric_key, 0.0)

    best = max(rows, key=score_for_row)
    selected_metric = weighted_metric_key if weighted_metric_key in best else fallback_metric_key
    selected_score = best.get(selected_metric, 0.0)
    caption = best["content_pack"]["caption"]

    return {
        "goal": goal,
        "topic": best["topic"],
        "hook": best["selected_hook"],
        "caption": caption,
        "hashtags": _extract_hashtags(caption),
        "why_selected": (
            f"Highest {goal} using {selected_metric} ({selected_score}) "
            f"with strong postability ({best.get('postability_score', 0.0)})."
        ),
        "best_window": best_window,
    }


def build_mobile_command_center_export(
    output_path: str = "data/exports/mobile_command_center.json",
    source_rows_path: str = "data/exports/daily_content_sheet.json",
    engine_recommendations_path: str = "data/exports/engine_recommendations.json",
) -> dict:

    rows_path = Path(source_rows_path)

    if not rows_path.exists():
        raise FileNotFoundError(f"Missing source rows JSON: {rows_path}")

    rows = json.loads(rows_path.read_text(encoding="utf-8"))

    if not rows:
        raise ValueError(f"No rows found in source rows JSON: {rows_path}")

    window = _best_window(Path(engine_recommendations_path))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_source": str(rows_path),
        "recommendations": {
            "views": _card_for_goal(rows, "views", "weighted_view_score", "view_score", window),
            "followers": _card_for_goal(rows, "followers", "weighted_follow_score", "follow_score", window),
            "shares": _card_for_goal(rows, "shares", "weighted_share_score", "share_score", window),
        },
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "mobile_command_center_output": str(out),
        "generated_at": payload["generated_at"],
        "run_source": str(rows_path),
    }


def refresh_mobile_command_center(run_engine: bool = True) -> dict:
    refreshed_paths: dict[str, str] = {}

    if run_engine:
        refreshed_paths = simulate_daily_content_sheet()

    export_result = build_mobile_command_center_export()

    return {
        "refreshed": run_engine,
        "pipeline": refreshed_paths,
        **export_result,
    }
