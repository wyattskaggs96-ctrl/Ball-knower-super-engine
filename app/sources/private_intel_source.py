from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.label_config import PRIVATE_INTEL_LABELS
from app.sources.trend_item import NormalizedTrendItem
from app.sources.trend_normalizer import compute_trend_weight

DEFAULT_PRIVATE_INTEL_PATH = Path(__file__).resolve().parents[2] / "data" / "private_intel.json"
NOTE_TYPES = PRIVATE_INTEL_LABELS["note_type"]
URGENCY_LEVELS = PRIVATE_INTEL_LABELS["urgency"]
CONFIDENCE_LEVELS = PRIVATE_INTEL_LABELS["confidence"]
CONFIDENCE_TO_SCORE = {"low": 0.4, "medium": 0.7, "high": 0.9}


class PrivateIntelItem(BaseModel):
    source: str
    article_url: str | None = None
    title: str
    summary: str = ""
    team_tags: list[str] = Field(default_factory=list)
    player_tags: list[str] = Field(default_factory=list)
    urgency: str = "medium"
    confidence: str | float = "medium"
    note_type: str = "other"

    @field_validator("urgency")
    @classmethod
    def _validate_urgency(cls, value: str) -> str:
        lowered = value.lower().strip()
        if lowered not in URGENCY_LEVELS:
            raise ValueError(f"urgency must be one of {sorted(URGENCY_LEVELS)}")
        return lowered

    @field_validator("note_type")
    @classmethod
    def _validate_note_type(cls, value: str) -> str:
        lowered = value.lower().strip()
        if lowered not in NOTE_TYPES:
            raise ValueError(f"note_type must be one of {sorted(NOTE_TYPES)}")
        return lowered

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: str | float) -> str | float:
        if isinstance(value, (int, float)):
            numeric = float(value)
            if numeric < 0.0 or numeric > 1.0:
                raise ValueError("numeric confidence must be between 0.0 and 1.0")
            return round(numeric, 2)

        lowered = value.lower().strip()
        if lowered not in CONFIDENCE_LEVELS:
            raise ValueError(f"confidence must be one of {sorted(CONFIDENCE_LEVELS)} or numeric 0..1")
        return lowered

    @property
    def confidence_score(self) -> float:
        if isinstance(self.confidence, (int, float)):
            return float(self.confidence)
        return CONFIDENCE_TO_SCORE[self.confidence]


def load_private_intel(data_path: str | Path = DEFAULT_PRIVATE_INTEL_PATH) -> list[PrivateIntelItem]:
    path = Path(data_path)
    if not path.exists():
        return []

    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("private_intel.json must be a JSON list")

    return [PrivateIntelItem.model_validate(item) for item in payload]


def _private_intel_source_multiplier(note_type: str) -> float:
    if note_type in {"recruiting", "transfer_portal", "rumor"}:
        return 1.25
    if note_type in {"breaking_news", "injury", "coaching"}:
        return 1.15
    return 1.05


def normalize_private_intel_items(items: list[PrivateIntelItem]) -> list[NormalizedTrendItem]:
    normalized: list[NormalizedTrendItem] = []
    for item in items:
        base_weight = compute_trend_weight(item.note_type, item.urgency)
        confidence_boost = 0.2 + (item.confidence_score * 0.5)
        source_multiplier = _private_intel_source_multiplier(item.note_type)
        trend_weight = round(base_weight * source_multiplier * confidence_boost, 2)

        normalized.append(
            NormalizedTrendItem(
                source=item.source,
                source_type="private_intel",
                title=" ".join(item.title.split()),
                url=item.article_url,
                summary=item.summary,
                team_tags=item.team_tags,
                player_tags=item.player_tags,
                topic_type=item.note_type,
                urgency=item.urgency,
                trend_weight=trend_weight,
            )
        )

    return normalized
