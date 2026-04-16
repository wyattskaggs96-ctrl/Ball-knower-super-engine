from app.core.models import TrendCandidate
from app.core.scoring import ScoringEngine


def test_scoring_structure():
    trend = TrendCandidate(source="rss", topic="NBA trade drama", summary="big debate", sport="basketball")
    score = ScoringEngine().score(trend)
    expected = {
        "recency",
        "audience_fit",
        "virality",
        "controversy",
        "recognition",
        "ease_of_execution",
        "total_score",
    }
    assert set(score.keys()) == expected
