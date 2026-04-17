from __future__ import annotations

import json
from pathlib import Path

from app.db.database import get_connection, init_db
from app.db.repository import Repository
from app.feedback.engine_integration import run_feedback_loop
from app.feedback.manual_intake import load_manual_posts
from app.feedback.metrics import add_post_metrics, build_grouped_performance
from app.feedback.normalize import normalize_posts


def test_load_manual_posts_parses_csv() -> None:
    result = load_manual_posts("data/manual_tiktok_analytics.csv")

    assert len(result.records) >= 10
    assert not result.errors
    assert result.records[0]["post_id"].startswith("bk_")
    assert isinstance(result.records[0]["teams_tagged"], list)


def test_load_manual_posts_handles_optional_fields(tmp_path: Path) -> None:
    sample = tmp_path / "manual.csv"
    sample.write_text(
        "post_id,post_timestamp,topic_type,hook_type,video_style,length_seconds,views\n"
        "row_1,2026-04-15T13:12:00Z,nba,stat_shock,facecam_breakdown,30,1000\n",
        encoding="utf-8",
    )

    result = load_manual_posts(sample)

    assert not result.errors
    assert result.records[0]["likes"] == 0
    assert result.records[0]["watch_time_seconds"] == 0


def test_manual_input_drives_metrics_and_recommendations() -> None:
    result = load_manual_posts("data/manual_tiktok_analytics.csv")
    posts = add_post_metrics(normalize_posts(result.records))
    grouped = build_grouped_performance(posts)

    assert grouped["topic_performance"]
    assert grouped["hook_performance"]
    assert grouped["topic_performance"][0]["avg_follower_conversion_rate"] >= grouped["topic_performance"][-1][
        "avg_follower_conversion_rate"
    ]


def test_feedback_run_with_manual_source_generates_outputs(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite3"
    export_dir = tmp_path / "exports"

    conn = get_connection(str(db_path))
    init_db(conn, "app/db/schema.sql")
    repo = Repository(conn)

    result = run_feedback_loop(
        repo,
        str(export_dir),
        source="manual",
        manual_file="data/manual_tiktok_analytics.csv",
    )

    payload = json.loads((export_dir / "engine_recommendations.json").read_text(encoding="utf-8"))

    assert Path(result["daily_feedback"]).exists()
    assert Path(result["goal_feedback_report"]).exists()
    assert payload["source"] == "manual"
    assert payload["recommendations"]
    assert payload["goal_aware_recommendations"]["views"]["topic_type"]["best"]["group_key"]
