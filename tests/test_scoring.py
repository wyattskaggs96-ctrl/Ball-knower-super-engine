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
        "clarity_1s_score",
        "star_power_score",
        "search_heat_score",
        "emotion_score",
        "pov_strength_score",
        "fan_identity_score",
        "rivalry_score",
        "sendability_score",
        "view_score",
        "follow_score",
        "share_score",
        "primary_goal",
        "total_score",
    }
    assert set(score.keys()) == expected
