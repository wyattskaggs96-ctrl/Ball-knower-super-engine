from __future__ import annotations

from app.agents.content_scorer import ContentScoringAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.script_generator import ScriptGeneratorAgent
from app.core.models import ContentPack, Hook, TrendScore


class ContentService:
    def __init__(
        self,
        scorer: ContentScoringAgent,
        hook_generator: HookGeneratorAgent,
        script_generator: ScriptGeneratorAgent,
    ) -> None:
        self.scorer = scorer
        self.hook_generator = hook_generator
        self.script_generator = script_generator

    def score(self, threshold: float) -> list[TrendScore]:
        return self.scorer.run(threshold=threshold)

    def generate_hooks(self, trend_id: int, count: int = 4) -> list[Hook]:
        return self.hook_generator.run(trend_id=trend_id, count=count)

    def generate_script(self, hook_id: int) -> ContentPack | None:
        return self.script_generator.run(hook_id=hook_id)
