from __future__ import annotations

MANUAL_ANALYTICS_LABELS = {
    "topic_type": {
        "nfl",
        "nba",
        "college_basketball",
        "college_football",
        "mlb",
        "golf",
        "recruiting",
        "transfer_portal",
        "off_topic",
    },
    "hook_type": {
        "fan_callout",
        "hot_take",
        "question",
        "news_reaction",
        "stat_shock",
        "funny_open",
    },
    "video_style": {
        "analyst_clip",
        "facecam_breakdown",
        "gameplay_text",
        "screenshot_reaction",
        "meme_edit",
        "quick_news",
    },
}

PRIVATE_INTEL_LABELS = {
    "note_type": {
        "recruiting",
        "transfer_portal",
        "injury",
        "coaching",
        "schedule",
        "rumor",
        "breaking_news",
        "matchup",
        "other",
    },
    "urgency": {"low", "medium", "high"},
    "confidence": {"low", "medium", "high"},
}
