from app.feedback.insights import generate_grouped_insights
from app.feedback.recommend import generate_recommendations


def test_generate_grouped_insights_and_recommendations() -> None:
    grouped = {
        "topic_performance": [
            {
                "group_key": "recruiting",
                "posts": 3,
                "avg_views": 20000,
                "avg_follower_conversion_rate": 0.011,
                "avg_engagement_rate": 0.085,
                "avg_completion_rate": 0.58,
            },
            {
                "group_key": "funny_clips",
                "posts": 3,
                "avg_views": 35000,
                "avg_follower_conversion_rate": 0.002,
                "avg_engagement_rate": 0.034,
                "avg_completion_rate": 0.24,
            },
        ],
        "hook_performance": [],
        "timing_performance": [],
        "length_performance": [],
        "video_style_performance": [],
    }

    insights = generate_grouped_insights(grouped)
    recommendations = generate_recommendations(grouped)

    assert any("prioritize 'recruiting'" in item["summary"] for item in insights)
    assert any(rec["action"] == "increase" and rec["focus"] == "recruiting" for rec in recommendations)
    assert any(rec["action"] == "decrease" and rec["focus"] == "funny_clips" for rec in recommendations)
