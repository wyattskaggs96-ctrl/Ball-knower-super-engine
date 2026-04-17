from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

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
}


def _is_sports_relevant(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in SPORT_KEYWORDS)


def _infer_sport(text: str) -> str:
    lowered = text.lower()
    if "nba" in lowered:
        return "nba"
    if "nfl" in lowered:
        return "nfl"
    if "mlb" in lowered:
        return "mlb"
    if "nhl" in lowered:
        return "nhl"
    if "soccer" in lowered or "fifa" in lowered:
        return "soccer"
    if "ncaa" in lowered or "march madness" in lowered:
        return "college basketball"
    return "general"


def fetch_google_trends(timeout_seconds: int = 6, max_items: int = 20, geo: str = "US") -> list[TrendCandidate]:
    try:
        import requests
    except ModuleNotFoundError:
        logger.warning("requests is not installed; skipping Google Trends ingestion.")
        return []

    try:
        response = requests.get(
            "https://trends.google.com/trending/rss",
            params={"geo": geo},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Google Trends ingestion failed: %s", exc)
        return []

    try:
        root = ElementTree.fromstring(response.text)
    except ElementTree.ParseError as exc:
        logger.warning("Failed to parse Google Trends RSS: %s", exc)
        return []

    trends: list[TrendCandidate] = []
    for item in root.findall("./channel/item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or "").strip()
        joined_text = f"{title} {description}".strip()
        if not title or not _is_sports_relevant(joined_text):
            continue

        published_at = datetime.now(timezone.utc)
        pub_date_raw = item.findtext("pubDate")
        if pub_date_raw:
            try:
                published_at = parsedate_to_datetime(pub_date_raw).astimezone(timezone.utc)
            except (TypeError, ValueError):
                pass

        trends.append(
            TrendCandidate(
                source="google_trends",
                topic=title,
                summary=description or "Sports-related search interest trend.",
                url=(item.findtext("link") or "").strip() or None,
                sport=_infer_sport(joined_text),
                source_timestamp=published_at,
            )
        )

    return trends
