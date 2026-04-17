from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

from app.sources.trend_item import NormalizedTrendItem
from app.sources.trend_normalizer import normalize_trend_item

ESPN_PUBLIC_FEED_URL = "https://www.espn.com/espn/rss/news"
ESPN_FALLBACK_HEADLINES = [
    {
        "title": "NBA playoffs: late-game heroics spark finals pressure debate",
        "url": "https://www.espn.com/nba/",
        "summary": "Public fallback headline used when ESPN RSS is unavailable in this environment.",
    },
    {
        "title": "NFL draft buzz: teams weighing a surprise first-round trade",
        "url": "https://www.espn.com/nfl/draft/",
        "summary": "Public fallback headline used when ESPN RSS is unavailable in this environment.",
    },
]


def _fallback_items(limit: int) -> list[NormalizedTrendItem]:
    return [
        normalize_trend_item(
            source="espn",
            source_type="public_feed_fallback",
            title=row["title"],
            url=row["url"],
            summary=row["summary"],
        )
        for row in ESPN_FALLBACK_HEADLINES[:limit]
    ]


def fetch_trends(feed_url: str = ESPN_PUBLIC_FEED_URL, limit: int = 10, raw_feed: str | None = None) -> list[NormalizedTrendItem]:
    try:
        xml_payload = raw_feed
        if xml_payload is None:
            request = Request(feed_url, headers={"User-Agent": "BallKnowerEngine/1.0"})
            with urlopen(request, timeout=8) as response:
                xml_payload = response.read().decode("utf-8", errors="ignore")

        root = ET.fromstring(xml_payload or "")
        items = root.findall(".//item")[:limit]
        parsed = [
            normalize_trend_item(
                source="espn",
                source_type="public_feed",
                title=(item.findtext("title") or "ESPN headline").strip(),
                url=(item.findtext("link") or "").strip() or None,
                summary=(item.findtext("description") or "").strip(),
            )
            for item in items
            if (item.findtext("title") or "").strip()
        ]
        return parsed or _fallback_items(limit)
    except Exception:
        return _fallback_items(limit)
