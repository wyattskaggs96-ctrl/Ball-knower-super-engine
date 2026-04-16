from __future__ import annotations

from app.core.llm import LLMClient
from app.core.models import Hook
from app.core.prompts import HOOK_PROMPT
from app.db.repository import Repository


class HookGeneratorAgent:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    def _build_hooks(self, topic: str) -> list[str]:
        topic_clean = topic.strip().rstrip("?.!")
        return [
            f"Hot take: {topic_clean} — and people are scared to say it.",
            f"If you think {topic_clean.lower()} is obvious, you're missing the real problem.",
            f"This is why {topic_clean.lower()} could blow up by next week.",
            f"I have one question about {topic_clean.lower()} that nobody can answer.",
            f"Pick a side right now: {topic_clean.lower()} is genius or a total fumble?",
        ]

    def run(self, trend_id: int, count: int = 4) -> list[Hook]:
        trend = self.repo.get_trend_candidate(trend_id)
        if not trend:
            return []

        score = self.repo.latest_score_for_trend(trend_id)
        generated = self.llm.generate(HOOK_PROMPT, f"topic={trend.topic}; summary={trend.summary}")
        hooks = self._build_hooks(trend.topic)

        if "[mock-llm]" not in generated:
            hooks[0] = generated.splitlines()[0][:110]

        out: list[Hook] = []
        for hook_text in hooks[: max(3, min(count, 5))]:
            model = Hook(
                trend_candidate_id=trend_id,
                trend_score_id=score.id if score else None,
                hook_text=hook_text,
            )
            model.id = self.repo.insert_hook(model)
            out.append(model)
        return out
