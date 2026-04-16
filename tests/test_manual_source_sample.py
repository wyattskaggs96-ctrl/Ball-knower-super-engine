from app.sources.manual_source import fetch_trends


def test_manual_source_loads_sample_data_by_default():
    trends = fetch_trends()
    assert len(trends) >= 25
    assert any("portal" in t.topic.lower() for t in trends)
