from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from app.core.models import TrendCandidate


logger = logging.getLogger(__name__)


def _infer_sport_from_key(sport_key: str) -> str:
    lowered = sport_key.lower()
    if "nba" in lowered:
        return "nba"
    if "nfl" in lowered:
        return "nfl"
    if "mlb" in lowered:
        return "mlb"
    if "nhl" in lowered:
        return "nhl"
    if "soccer" in lowered:
        return "soccer"
    if "ncaa" in lowered:
        return "college basketball"
    return "general"


def fetch_odds_trends(timeout_seconds: int = 8, max_events: int = 20) -> list[TrendCandidate]:
    try:
        import requests
    except ModuleNotFoundError:
        logger.warning("requests is not installed; skipping odds trend ingestion.")
        return []

    api_key = os.getenv("ODDS_API_KEY", "").strip()
    if not api_key:
        logger.info("ODDS_API_KEY not set; skipping odds trend ingestion.")
        return []

    try:
        response = requests.get(
            "https://api.the-odds-api.com/v4/sports/upcoming/odds/",
            params={
                "apiKey": api_key,
                "regions": "us",
                "markets": "h2h",
                "oddsFormat": "american",
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Odds trend ingestion failed: %s", exc)
        return []

    trends: list[TrendCandidate] = []
    for event in payload[:max_events]:
        home_team = (event.get("home_team") or "").strip()
        away_team = (event.get("away_team") or "").strip()
        if not home_team or not away_team:
            continue

        sport_key = event.get("sport_key", "")
        commence_time_raw = event.get("commence_time")
        commence_time = datetime.now(timezone.utc)
        if commence_time_raw:
            try:
                commence_time = datetime.fromisoformat(commence_time_raw.replace("Z", "+00:00"))
            except ValueError:
                pass

        topic = f"Betting market watch: {away_team} vs {home_team}"
        summary = f"Upcoming odds market for {away_team} at {home_team}."
        trends.append(
            TrendCandidate(
                source="odds_api",
                topic=topic,
                summary=summary,
                url=None,
                sport=_infer_sport_from_key(sport_key),
                source_timestamp=commence_time,
            )
        )

    return trends
