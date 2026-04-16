from app.agents.script_generator import ScriptGeneratorAgent
from app.core.config import Settings
from app.core.llm import LLMClient
from app.core.models import Hook, TrendCandidate


class RepoStub:
    def get_hook(self, hook_id):
        return Hook(id=hook_id, trend_candidate_id=1, hook_text="Hot take incoming")

    def get_trend_candidate(self, trend_id):
        return TrendCandidate(id=trend_id, source="rss", topic="NBA upset", summary="x")

    def insert_content_pack(self, pack):
        return 1


def test_content_pack_structure():
    agent = ScriptGeneratorAgent(RepoStub(), LLMClient(Settings()))
    pack = agent.run(1)
    assert pack is not None
    assert isinstance(pack.overlay_lines, list)
    assert pack.caption
    assert pack.cta
    assert pack.creator_notes
