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

    def _keyword_score(self, text: str, terms: list[str], base: float = 55.0, boost: float = 8.0, cap: float = 95.0) -> float:
        hits = sum(1 for term in terms if term in text)
        return min(cap, base + hits * boost)

    def score(self, trend: TrendCandidate) -> dict:
        topic = trend.topic.lower()
        summary = trend.summary.lower()
        text = f"{topic} {summary}"

        recency = 90.0
        audience_fit = 85.0 if trend.sport != "general" else 70.0
        virality = 88.0 if any(k in topic for k in ["trade", "injury", "drama", "finals"]) else 65.0
        controversy = 80.0 if any(k in summary for k in ["debate", "controvers", "hot take"]) else 50.0
        recognition = 85.0 if any(k in topic for k in ["nba", "nfl", "mlb", "fifa", "ufc"]) else 60.0
        ease_of_execution = 75.0

        broad_audience_score = 90.0 if trend.sport in {"nba", "nfl", "mlb", "soccer"} else 72.0
        if any(k in text for k in ["lakers", "cowboys", "chiefs", "celtics", "warriors"]):
            broad_audience_score = min(96.0, broad_audience_score + 6.0)

        clarity_1s_score = self._keyword_score(
            text,
            ["why", "what this means", "explained", "breakdown", "simple", "nobody wants to admit", "in plain sight"],
            base=60.0,
            boost=6.0,
        )
        star_power_score = self._keyword_score(
            text,
            ["lebron", "mahomes", "curry", "messi", "brady", "lakers", "cowboys", "chiefs", "warriors", "celtics"],
            base=58.0,
            boost=9.0,
        )
        search_heat_score = self._keyword_score(
            text,
            ["trade", "injury", "breaking", "finals", "playoffs", "draft", "decommit", "portal", "mvp"],
            base=56.0,
            boost=7.0,
        )
        emotion_score = self._keyword_score(
            text,
            ["drama", "outrage", "shock", "hate", "love", "clutch", "choke", "chaos", "panic", "exposed"],
            base=56.0,
            boost=7.5,
        )
        pov_strength_score = self._keyword_score(
            text,
            ["my take", "unpopular", "rank", "ranking", "prediction", "predict", "should", "must", "fake", "myth"],
            base=58.0,
            boost=7.0,
        )
        explanation_score = self._keyword_score(
            text,
            ["what this means", "because", "why", "how", "context", "explained", "breakdown", "matters more"],
            base=57.0,
            boost=6.5,
        )
        fan_identity_score = self._keyword_score(
            text,
            ["real fans", "casual", "fanbase", "legacy", "goat", "respect", "culture", "identity", "pressure"],
            base=56.0,
            boost=7.0,
        )
        rivalry_score = self._keyword_score(
            text,
            ["vs", "rivalry", "beef", "lakers", "celtics", "yankees", "mets", "cowboys", "eagles", "jets", "chiefs"],
            base=54.0,
            boost=8.0,
        )
        disrespect_score = self._keyword_score(
            text,
            ["fake", "cooked", "overrated", "panic", "myth", "exposed", "ruined", "closing", "suspect"],
            base=55.0,
            boost=7.5,
        )
        receipts_score = self._keyword_score(
            text,
            ["receipts", "proof", "numbers", "clips", "stat", "evidence", "in plain sight", "nobody wants to admit"],
            base=54.0,
            boost=7.0,
        )
        validation_score = self._keyword_score(
            text,
            ["fans say", "fans think", "nobody wants to admit", "all-in", "pressure", "split on", "argue"],
            base=55.0,
            boost=6.5,
        )
        sendability_score = self._keyword_score(
            text,
            ["receipts", "proof", "show this", "send this", "debate", "disrespect", "exposed", "argue", "group chat"],
            base=55.0,
            boost=7.5,
        )

        view_score = round(
            broad_audience_score * 0.25
            + clarity_1s_score * 0.16
            + star_power_score * 0.18
            + search_heat_score * 0.19
            + emotion_score * 0.12
            + virality * 0.1,
            2,
        )
        follow_score = round(
            pov_strength_score * 0.28
            + explanation_score * 0.24
            + fan_identity_score * 0.2
            + clarity_1s_score * 0.12
            + audience_fit * 0.1
            + recency * 0.06,
            2,
        )
        share_score = round(
            rivalry_score * 0.2
            + disrespect_score * 0.2
            + emotion_score * 0.12
            + receipts_score * 0.16
            + validation_score * 0.14
            + sendability_score * 0.18,
            2,
        )
        primary_goal = max(
            [("views", view_score), ("followers", follow_score), ("shares", share_score)],
            key=lambda item: item[1],
        )[0]

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
            "clarity_1s_score": round(clarity_1s_score, 2),
            "star_power_score": round(star_power_score, 2),
            "search_heat_score": round(search_heat_score, 2),
            "emotion_score": round(emotion_score, 2),
            "pov_strength_score": round(pov_strength_score, 2),
            "fan_identity_score": round(fan_identity_score, 2),
            "rivalry_score": round(rivalry_score, 2),
            "sendability_score": round(sendability_score, 2),
            "view_score": view_score,
            "follow_score": follow_score,
            "share_score": share_score,
            "primary_goal": primary_goal,
            "total_score": round(total, 2),
        }
