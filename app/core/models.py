from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class TrendCandidate(BaseModel):
    id: Optional[int] = None
    source: str
    topic: str
    summary: str
    url: Optional[str] = None
    sport: str = "general"
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fingerprint: Optional[str] = None


class TrendScore(BaseModel):
    id: Optional[int] = None
    trend_candidate_id: int
    recency: float
    audience_fit: float
    virality: float
    controversy: float
    recognition: float
    ease_of_execution: float
    clarity_1s_score: float = 0.0
    star_power_score: float = 0.0
    search_heat_score: float = 0.0
    emotion_score: float = 0.0
    pov_strength_score: float = 0.0
    fan_identity_score: float = 0.0
    rivalry_score: float = 0.0
    sendability_score: float = 0.0
    view_score: float = 0.0
    follow_score: float = 0.0
    share_score: float = 0.0
    primary_goal: str = "views"
    total_score: float
    reasoning: str = ""
    recommended: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Hook(BaseModel):
    id: Optional[int] = None
    trend_candidate_id: int
    trend_score_id: Optional[int] = None
    hook_text: str
    style: str = "tiktok"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContentPack(BaseModel):
    id: Optional[int] = None
    trend_candidate_id: int
    hook_id: int
    overlay_lines: List[str]
    caption: str
    cta: str
    creator_notes: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
