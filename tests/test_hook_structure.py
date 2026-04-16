from app.agents.hook_generator import HookGeneratorAgent
from app.core.llm import LLMClient
from app.core.models import TrendCandidate
from app.core.config import Settings


class RepoStub:
    def get_trend_candidate(self, trend_id):
        return TrendCandidate(id=trend_id, source="rss", topic="NBA finals upset", summary="x")

    def latest_score_for_trend(self, trend_id):
        return None

    def insert_hook(self, hook):
        return 1


def test_hook_output_structure():
    agent = HookGeneratorAgent(RepoStub(), LLMClient(Settings()))
    hooks = agent.run(1, count=4)
    assert 3 <= len(hooks) <= 5
    assert all(h.hook_text for h in hooks)
