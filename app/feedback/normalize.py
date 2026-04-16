from __future__ import annotations

from datetime import datetime
from typing import Any


NUMERIC_FIELDS = {
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "profile_views",
    "followers_gained",
    "watch_time",
    "watch_time_seconds",
    "completion_rate",
    "length_seconds",
}


def _posting_window(hour: int) -> str:
    if 5 <= hour < 10:
        return "morning"
    if 10 <= hour < 15:
        return "midday"
    if 15 <= hour < 19:
        return "afternoon"
    if 19 <= hour < 23:
        return "evening"
    return "late_night"


def _length_bucket(length_seconds: float) -> str:
    if length_seconds < 20:
        return "short"
    if length_seconds <= 45:
        return "medium"
    return "long"


def normalize_posts(raw_posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for post in raw_posts:
        item = dict(post)
        for field in NUMERIC_FIELDS:
            item[field] = float(item.get(field, 0) or 0)

        item.setdefault("post_id", "")
        item.setdefault("post_url", "")
        item["watch_time"] = float(item.get("watch_time", item.get("watch_time_seconds", 0)) or 0)

        timestamp = datetime.fromisoformat(str(item["post_timestamp"]).replace("Z", "+00:00"))
        item["post_timestamp"] = timestamp.isoformat()
        item["posting_hour"] = timestamp.hour
        item["posting_window"] = _posting_window(timestamp.hour)
        item["length_bucket"] = _length_bucket(item["length_seconds"])
        item["teams_tagged"] = item.get("teams_tagged") or []
        item["players_tagged"] = item.get("players_tagged") or []

        normalized.append(item)
    return normalized
