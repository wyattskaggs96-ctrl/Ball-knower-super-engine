from __future__ import annotations

import logging
import os
from typing import Any


from app.core.models import TrendCandidate


logger = logging.getLogger(__name__)

SPORT_KEYWORDS = {
    "nba",
    "nfl",
    "mlb",
    "nhl",
    "wnba",
    "ncaa",
    "soccer",
    "football",
    "basketball",
    "baseball",
    "hockey",
    "playoffs",
    "finals",
    "super bowl",
    "march madness",
    "ufc",
    "mma",
    "golf",
    "tennis",
    "fifa",
    "premier league",
    "champions league",
    "olympics",
}

SPORT_HINTS = {
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


def _is_sports_relevant(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in SPORT_KEYWORDS)


def _infer_sport(text: str) -> str:
    lowered = text.lower()
    for hint, sport in SPORT_HINTS.items():
        if hint in lowered:
            return sport
    return "general"


def _article_to_trend(article: dict[str, Any]) -> TrendCandidate | None:
    title = (article.get("title") or "").strip()
    description = (article.get("description") or "").strip()
    joined_text = f"{title} {description}".strip()

    if not title or not _is_sports_relevant(joined_text):
        return None

    source_name = article.get("source", {}).get("name") or "newsapi"
    summary = description or "Live sports headline from NewsAPI."

    return TrendCandidate(
        source=f"live:{source_name}",
        topic=title,
        summary=summary,
        sport=_infer_sport(joined_text),
        url=article.get("url"),
    )


def fetch_live_trends(timeout_seconds: int = 6, page_size: int = 25) -> list[TrendCandidate]:
    try:
        import requests
    except ModuleNotFoundError:
        logger.warning("requests is not installed; skipping live trend ingestion.")
        return []

    api_key = os.getenv("NEWS_API_KEY", "").strip()
    if not api_key:
        logger.info("NEWS_API_KEY not set; skipping live trend ingestion.")
        return []

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "category": "sports",
                "language": "en",
                "pageSize": page_size,
                "apiKey": api_key,
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Live trend ingestion failed: %s", exc)
        return []

    articles = payload.get("articles", [])
    trends: list[TrendCandidate] = []
    for article in articles:
        trend = _article_to_trend(article)
        if trend:
            trends.append(trend)

    return trends
