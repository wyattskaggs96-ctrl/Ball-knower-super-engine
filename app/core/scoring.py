from __future__ import annotations

from dataclasses import dataclass

from app.core.models import TrendCandidate


@dataclass
class ScoreWeights:
    recency: float = 0.20
    audience_fit: float = 0.20
    virality: float = 0.20
    controversy: float = 0.10
    recognition: float = 0.15
    ease_of_execution: float = 0.15


class ScoringEngine:
    def __init__(self, weights: ScoreWeights | None = None) -> None:
        self.weights = weights or ScoreWeights()

    def score(self, trend: TrendCandidate) -> dict:
        topic = trend.topic.lower()
        summary = trend.summary.lower()

        recency = 90.0
        audience_fit = 85.0 if trend.sport != "general" else 70.0
        virality = 88.0 if any(k in topic for k in ["trade", "injury", "drama", "finals"]) else 65.0
        controversy = 80.0 if any(k in summary for k in ["debate", "controvers", "hot take"]) else 50.0
        recognition = 85.0 if any(k in topic for k in ["nba", "nfl", "mlb", "fifa", "ufc"]) else 60.0
        ease_of_execution = 75.0

        total = (
            recency * self.weights.recency
            + audience_fit * self.weights.audience_fit
            + virality * self.weights.virality
            + controversy * self.weights.controversy
            + recognition * self.weights.recognition
            + ease_of_execution * self.weights.ease_of_execution
        )

        return {
            "recency": recency,
            "audience_fit": audience_fit,
            "virality": virality,
            "controversy": controversy,
            "recognition": recognition,
            "ease_of_execution": ease_of_execution,
            "total_score": round(total, 2),
        }
