from __future__ import annotations

from app.core.llm import LLMClient
from app.core.models import TrendScore
from app.core.prompts import HOOK_PROMPT
from app.core.scoring import ScoringEngine
from app.db.repository import Repository


class ContentScoringAgent:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm
        self.engine = ScoringEngine()

    def run(self, threshold: float) -> list[TrendScore]:
        trends = self.repo.list_trend_candidates()
        results: list[TrendScore] = []
        for trend in trends:
            scored = self.engine.score(trend)
            reasoning = self.llm.generate(HOOK_PROMPT, f"Trend: {trend.topic} | Summary: {trend.summary}")
            model = TrendScore(
                trend_candidate_id=trend.id,
                reasoning=reasoning,
                recommended=scored["total_score"] >= threshold,
                **scored,
            )
            model.id = self.repo.insert_trend_score(model)
            results.append(model)
        return [r for r in results if r.recommended]
