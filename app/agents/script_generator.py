from __future__ import annotations

from app.core.llm import LLMClient
from app.core.models import ContentPack
from app.core.prompts import SCRIPT_PROMPT
from app.db.repository import Repository


class ScriptGeneratorAgent:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    def run(self, hook_id: int) -> ContentPack | None:
        hook = self.repo.get_hook(hook_id)
        if not hook:
            return None
        trend = self.repo.get_trend_candidate(hook.trend_candidate_id)
        if not trend:
            return None

        _ = self.llm.generate(SCRIPT_PROMPT, hook.hook_text)
        pack = ContentPack(
            trend_candidate_id=trend.id,
            hook_id=hook.id,
            overlay_lines=[
                hook.hook_text,
                f"Context: {trend.topic}",
                "Drop your take below 👇",
            ],
            caption=f"{hook.hook_text} #sports #fyp",
            cta="Comment your hottest take and follow for daily sports breakdowns.",
            creator_notes="Keep first 2 seconds punchy. Use stat graphic at 0:04. End with opinion split question.",
        )
        pack.id = self.repo.insert_content_pack(pack)
        return pack
