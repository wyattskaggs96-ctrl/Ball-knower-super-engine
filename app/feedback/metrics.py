from __future__ import annotations

from collections import defaultdict
from statistics import mean


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def add_post_metrics(posts: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for post in posts:
        views = float(post.get("views", 0.0))
        item = dict(post)
        item["follower_conversion_rate"] = _safe_div(float(post.get("followers_gained", 0.0)), views)
        item["engagement_rate"] = _safe_div(
            float(post.get("likes", 0.0)) + float(post.get("comments", 0.0)) + float(post.get("shares", 0.0)),
            views,
        )
        item["comment_rate"] = _safe_div(float(post.get("comments", 0.0)), views)
        item["share_rate"] = _safe_div(float(post.get("shares", 0.0)), views)
        item["save_rate"] = _safe_div(float(post.get("saves", 0.0)), views)
        enriched.append(item)
    return enriched


def build_grouped_performance(posts: list[dict]) -> dict[str, list[dict]]:
    groups = {
        "topic_performance": "topic_type",
        "hook_performance": "hook_type",
        "timing_performance": "posting_window",
        "length_performance": "length_bucket",
        "video_style_performance": "video_style",
    }

    grouped_output: dict[str, list[dict]] = {}
    for metric_name, key_field in groups.items():
        bucket: dict[str, list[dict]] = defaultdict(list)
        for post in posts:
            bucket[str(post.get(key_field, "unknown"))].append(post)

        summary_rows = []
        for key, rows in bucket.items():
            summary_rows.append(
                {
                    "group_key": key,
                    "posts": len(rows),
                    "avg_views": mean(r["views"] for r in rows),
                    "avg_followers_gained": mean(r["followers_gained"] for r in rows),
                    "avg_shares": mean(r["shares"] for r in rows),
                    "avg_follower_conversion_rate": mean(r["follower_conversion_rate"] for r in rows),
                    "avg_engagement_rate": mean(r["engagement_rate"] for r in rows),
                    "avg_completion_rate": mean(r["completion_rate"] for r in rows),
                }
            )

        grouped_output[metric_name] = sorted(
            summary_rows,
            key=lambda r: (r["avg_follower_conversion_rate"], r["avg_engagement_rate"], r["avg_views"]),
            reverse=True,
        )

    return grouped_output
