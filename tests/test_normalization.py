from app.core.utils import normalize_topic


def test_normalize_topic():
    assert normalize_topic("  NBA Finals!!! Rotation Debate ") == "nba finals rotation debate"
