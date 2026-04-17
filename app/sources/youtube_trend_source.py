from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from app.core.models import TrendCandidate


logger = logging.getLogger(__name__)


def _infer_sport(text: str) -> str:
    lowered = text.lower()
    mapping = {
        "nba": "nba",
        "nfl": "nfl",
        "mlb": "mlb",
        "nhl": "nhl",
        "wnba": "wnba",
        "ncaa": "college basketball",
        "soccer": "soccer",
        "football": "football",
        "basketball": "basketball",
        "baseball": "baseball",
        "hockey": "hockey",
        "ufc": "mma",
        "mma": "mma",
        "golf": "golf",
        "tennis": "tennis",
    }
    for key, sport in mapping.items():
        if key in lowered:
            return sport
    return "general"


def fetch_youtube_trends(timeout_seconds: int = 8, max_results: int = 20, region_code: str = "US") -> list[TrendCandidate]:
    try:
        import requests
    except ModuleNotFoundError:
        logger.warning("requests is not installed; skipping YouTube trend ingestion.")
        return []

    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        logger.info("YOUTUBE_API_KEY not set; skipping YouTube trend ingestion.")
        return []

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",
                "chart": "mostPopular",
                "videoCategoryId": "17",
                "regionCode": region_code,
                "maxResults": max_results,
                "key": api_key,
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("YouTube trend ingestion failed: %s", exc)
        return []

    trends: list[TrendCandidate] = []
    for row in payload.get("items", []):
        snippet = row.get("snippet", {})
        title = (snippet.get("title") or "").strip()
        if not title:
            continue

        published_at_raw = snippet.get("publishedAt")
        published_at = datetime.now(timezone.utc)
        if published_at_raw:
            try:
                published_at = datetime.fromisoformat(published_at_raw.replace("Z", "+00:00"))
            except ValueError:
                pass

        description = (snippet.get("description") or "").strip()
        video_id = row.get("id")
        url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None
        trends.append(
            TrendCandidate(
                source="youtube",
                topic=title,
                summary=description or "Trending sports video from YouTube.",
                url=url,
                sport=_infer_sport(f"{title} {description}"),
                source_timestamp=published_at,
            )
        )

    return trends
