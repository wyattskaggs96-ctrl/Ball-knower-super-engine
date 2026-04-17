from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

from app.sources.trend_item import NormalizedTrendItem
from app.sources.trend_normalizer import normalize_trend_item

ON3_PUBLIC_FEED_URL = "https://www.on3.com/feed/"
ON3_FALLBACK_HEADLINES = [
    {
        "title": "Recruiting prediction machine flips toward SEC defensive line prospect",
        "url": "https://www.on3.com/college/",
        "summary": "Public fallback headline used when On3 feed is unavailable in this environment.",
    },
    {
        "title": "Transfer portal watch: veteran quarterback visiting two Power Four programs",
        "url": "https://www.on3.com/transfer-portal/",
        "summary": "Public fallback headline used when On3 feed is unavailable in this environment.",
    },
]


def _fallback_items(limit: int) -> list[NormalizedTrendItem]:
    return [
        normalize_trend_item(
            source="on3",
            source_type="public_feed_fallback",
            title=row["title"],
            url=row["url"],
            summary=row["summary"],
        )
        for row in ON3_FALLBACK_HEADLINES[:limit]
    ]


def fetch_trends(feed_url: str = ON3_PUBLIC_FEED_URL, limit: int = 10, raw_feed: str | None = None) -> list[NormalizedTrendItem]:
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
                source="on3",
                source_type="public_feed",
                title=(item.findtext("title") or "On3 headline").strip(),
                url=(item.findtext("link") or "").strip() or None,
                summary=(item.findtext("description") or "").strip(),
            )
            for item in items
            if (item.findtext("title") or "").strip()
        ]
        return parsed or _fallback_items(limit)
    except Exception:
        return _fallback_items(limit)
