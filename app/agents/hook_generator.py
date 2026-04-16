from __future__ import annotations

from app.core.llm import LLMClient
from app.core.models import Hook
from app.core.prompts import HOOK_PROMPT
from app.db.repository import Repository


class HookGeneratorAgent:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    def _mock_hooks(self, topic: str) -> list[str]:
        return [
            f"Everyone missed this about {topic}",
            f"Hot take: {topic} changes everything",
            f"The real reason {topic} is blowing up right now",
            f"This {topic} debate is way bigger than you think",
        ]

    def run(self, trend_id: int, count: int = 4) -> list[Hook]:
        trend = self.repo.get_trend_candidate(trend_id)
        if not trend:
            return []

        score = self.repo.latest_score_for_trend(trend_id)
        generated = self.llm.generate(HOOK_PROMPT, trend.topic)
        hooks = self._mock_hooks(trend.topic)
        if "[mock-llm]" not in generated:
            hooks[0] = generated[:90]

        out: list[Hook] = []
        for hook_text in hooks[: max(3, min(count, 5))]:
            model = Hook(trend_candidate_id=trend_id, trend_score_id=score.id if score else None, hook_text=hook_text)
            model.id = self.repo.insert_hook(model)
            out.append(model)
        return out
