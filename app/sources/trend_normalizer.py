from __future__ import annotations

import re

from app.sources.trend_item import NormalizedTrendItem


TEAM_PATTERN = re.compile(r"\b([A-Z][a-z]+\s(?:[A-Z][a-z]+|[A-Z]{2,}))\b")
PLAYER_PATTERN = re.compile(r"\b([A-Z][a-z]+\s[A-Z][a-z]+)\b")

TOPIC_KEYWORDS = {
    "transfer_portal": ("portal", "transfer", "commits", "decommit"),
    "recruiting": ("recruit", "recruiting", "commitment", "prospect"),
    "injury": ("injury", "out", "questionable", "returns"),
    "championship": ("playoff", "finals", "championship", "title"),
    "breaking_news": ("breaking", "trade", "fired", "suspended"),
}


def classify_topic_type(text: str) -> str:
    lowered = text.lower()
    for topic_type, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return topic_type
    return "general"


def infer_urgency(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("breaking", "urgent", "suspended", "fired", "trade")):
        return "high"
    if any(word in lowered for word in ("watch", "update", "heating up", "rumor")):
        return "medium"
    return "low"


def compute_trend_weight(topic_type: str, urgency: str) -> float:
    base = {
        "breaking_news": 1.5,
        "championship": 1.35,
        "transfer_portal": 1.25,
        "recruiting": 1.2,
        "injury": 1.15,
        "general": 1.0,
    }.get(topic_type, 1.0)
    if urgency == "high":
        return round(base + 0.4, 2)
    if urgency == "low":
        return round(base - 0.1, 2)
    return round(base, 2)


def normalize_trend_item(
    source: str,
    source_type: str,
    title: str,
    url: str | None,
    summary: str = "",
    team_tags: list[str] | None = None,
    player_tags: list[str] | None = None,
    topic_type: str | None = None,
    urgency: str | None = None,
) -> NormalizedTrendItem:
    cleaned_title = " ".join(title.split())
    joined_text = f"{cleaned_title} {summary}".strip()

    inferred_topic_type = topic_type or classify_topic_type(joined_text)
    inferred_urgency = urgency or infer_urgency(joined_text)

    inferred_teams = team_tags or sorted(set(match.strip() for match in TEAM_PATTERN.findall(cleaned_title)))
    inferred_players = player_tags or sorted(set(match.strip() for match in PLAYER_PATTERN.findall(cleaned_title)))

    return NormalizedTrendItem(
        source=source,
        source_type=source_type,
        title=cleaned_title,
        url=url,
        summary=summary,
        team_tags=inferred_teams,
        player_tags=inferred_players,
        topic_type=inferred_topic_type,
        urgency=inferred_urgency,
        trend_weight=compute_trend_weight(inferred_topic_type, inferred_urgency),
    )


def title_fingerprint(title: str) -> str:
    lowered = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    tokens = [token for token in lowered.split() if len(token) > 2]
    return " ".join(tokens)
