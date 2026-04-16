from __future__ import annotations

from app.core.config import Settings


class LLMClient:
    """Centralized LLM wrapper.

    V1 uses deterministic mock output by default and leaves room for real provider integration.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, prompt: str, context: str) -> str:
        if not self.settings.use_llm:
            return f"[mock-llm] {context[:180]}"

        # Placeholder for real API integrations.
        # Implementations can branch on self.settings.llm_provider.
        return f"[simulated-{self.settings.llm_provider}] {context[:180]}"
