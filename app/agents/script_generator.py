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

        _ = self.llm.generate(SCRIPT_PROMPT, f"hook={hook.hook_text}; trend={trend.topic}")

        pack = ContentPack(
            trend_candidate_id=trend.id,
            hook_id=hook.id,
            overlay_lines=[
                "BALL KNOWER ALERT 🚨",
                hook.hook_text,
                f"Topic: {trend.topic}",
                "Receipts in 3 points. Pick a side.",
            ],
            caption=(
                f"{hook.hook_text} This take is dividing real fans. "
                "Are we overrating narratives or ignoring obvious flaws? #ballknower #sportsdebate #fyp"
            ),
            cta="Drop your verdict in one sentence and tag the friend who argues this every week.",
            creator_notes=(
                "Open with hook in first 1.5s. Use hard cut to stat/clip at 0:03. "
                "Deliver point-counterpoint quickly, then force a binary poll at the end."
            ),
        )
        pack.id = self.repo.insert_content_pack(pack)
        return pack
