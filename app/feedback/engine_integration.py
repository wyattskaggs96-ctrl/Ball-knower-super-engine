from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.db.repository import Repository
from app.feedback.ingest import load_mock_posts
from app.feedback.insights import generate_grouped_insights
from app.feedback.metrics import add_post_metrics, build_grouped_performance
from app.feedback.normalize import normalize_posts
from app.feedback.recommend import generate_recommendations
from app.feedback.scheduler import schedule_stub


def _write_markdown(path: Path, title: str, lines: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join([f"# {title}", "", *[f"- {line}" for line in lines], ""])
    path.write_text(content, encoding="utf-8")
    return str(path)


def _persist_run(
    repo: Repository,
    posts: list[dict],
    grouped_performance: dict[str, list[dict]],
    insights: list[dict],
    recommendations: list[dict],
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = repo.conn.execute(
        "INSERT INTO agent_runs (agent_name, status, run_started_at, run_finished_at, notes) VALUES (?, ?, ?, ?, ?)",
        ("feedback_loop_agent", "completed", now, now, "mock feedback run"),
    )
    run_id = int(cur.lastrowid)

    for post in posts:
        post_cur = repo.conn.execute(
            """
            INSERT INTO posts (platform, post_timestamp, views, likes, comments, shares, saves, profile_views,
                               followers_gained, watch_time, completion_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "tiktok",
                post["post_timestamp"],
                post["views"],
                post["likes"],
                post["comments"],
                post["shares"],
                post["saves"],
                post["profile_views"],
                post["followers_gained"],
                post["watch_time"],
                post["completion_rate"],
            ),
        )
        post_id = int(post_cur.lastrowid)
        repo.conn.execute(
            """
            INSERT INTO post_metadata (post_id, hook_type, topic_type, length_seconds, teams_tagged, players_tagged, video_style)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                post["hook_type"],
                post["topic_type"],
                post["length_seconds"],
                json.dumps(post.get("teams_tagged", [])),
                json.dumps(post.get("players_tagged", [])),
                post["video_style"],
            ),
        )
        repo.conn.execute(
            """
            INSERT INTO performance_metrics (post_id, follower_conversion_rate, engagement_rate, comment_rate, share_rate, save_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                post["follower_conversion_rate"],
                post["engagement_rate"],
                post["comment_rate"],
                post["share_rate"],
                post["save_rate"],
                now,
            ),
        )

    for group_type, rows in grouped_performance.items():
        for row in rows:
            repo.conn.execute(
                """
                INSERT INTO grouped_insights (run_id, insight_type, insight_key, posts_count, avg_views,
                    avg_follower_conversion_rate, avg_engagement_rate, avg_completion_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    group_type,
                    row["group_key"],
                    row["posts"],
                    row["avg_views"],
                    row["avg_follower_conversion_rate"],
                    row["avg_engagement_rate"],
                    row["avg_completion_rate"],
                    now,
                ),
            )

    for rec in recommendations:
        repo.conn.execute(
            """
            INSERT INTO engine_recommendations (run_id, engine_target, action, focus, reason, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, rec["engine_target"], rec["action"], rec["focus"], rec["reason"], "high", now),
        )

    for insight in insights:
        repo.conn.execute(
            "UPDATE agent_runs SET notes = notes || ? WHERE id = ?",
            (f" | {insight['summary']}", run_id),
        )

    repo.conn.commit()
    return run_id


def run_feedback_loop(repo: Repository, export_dir: str) -> dict[str, str]:
    posts = add_post_metrics(normalize_posts(load_mock_posts()))
    grouped_performance = build_grouped_performance(posts)
    insights = generate_grouped_insights(grouped_performance)
    recommendations = generate_recommendations(grouped_performance)

    run_id = _persist_run(repo, posts, grouped_performance, insights, recommendations)

    export_path = Path(export_dir)
    daily_lines = [*map(lambda i: i["summary"], insights)] + [
        f"Run ID: {run_id}",
        f"Scheduler interval: {schedule_stub()['interval']}",
    ]
    daily_feedback = _write_markdown(export_path / "daily_feedback.md", "Daily Feedback", daily_lines)

    weekly_lines = [
        "Top priorities for next cycle:",
        *[f"{rec['action']} {rec['focus']} for {rec['engine_target']}" for rec in recommendations[:8]],
    ]
    weekly_review = _write_markdown(export_path / "weekly_review.md", "Weekly Review", weekly_lines)

    json_path = export_path / "engine_recommendations.json"
    json_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "recommendations": recommendations,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "daily_feedback": daily_feedback,
        "weekly_review": str(weekly_review),
        "engine_recommendations": str(json_path),
    }


def feedback_report(export_dir: str) -> str:
    target = Path(export_dir) / "weekly_review.md"
    if not target.exists():
        return f"No weekly review found at {target}"
    return target.read_text(encoding="utf-8")
