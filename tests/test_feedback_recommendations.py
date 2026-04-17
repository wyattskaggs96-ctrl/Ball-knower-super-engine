from app.feedback.insights import generate_grouped_insights
from app.feedback.recommend import build_goal_recommendation_groups, generate_recommendations


def test_generate_grouped_insights_and_recommendations() -> None:
    grouped = {
        "topic_performance": [
            {
                "group_key": "recruiting",
                "posts": 3,
                "avg_views": 20000,
                "avg_followers_gained": 120,
                "avg_shares": 400,
                "avg_follower_conversion_rate": 0.011,
                "avg_engagement_rate": 0.085,
                "avg_completion_rate": 0.58,
            },
            {
                "group_key": "funny_clips",
                "posts": 3,
                "avg_views": 35000,
                "avg_followers_gained": 40,
                "avg_shares": 900,
                "avg_follower_conversion_rate": 0.002,
                "avg_engagement_rate": 0.034,
                "avg_completion_rate": 0.24,
            },
        ],
        "hook_performance": [
            {
                "group_key": "stat_shock",
                "posts": 2,
                "avg_views": 21000,
                "avg_followers_gained": 140,
                "avg_shares": 320,
                "avg_follower_conversion_rate": 0.012,
                "avg_engagement_rate": 0.07,
                "avg_completion_rate": 0.55,
            },
            {
                "group_key": "question",
                "posts": 2,
                "avg_views": 50000,
                "avg_followers_gained": 50,
                "avg_shares": 1200,
                "avg_follower_conversion_rate": 0.003,
                "avg_engagement_rate": 0.04,
                "avg_completion_rate": 0.22,
            },
        ],
        "timing_performance": [],
        "length_performance": [],
        "video_style_performance": [
            {
                "group_key": "facecam_breakdown",
                "posts": 2,
                "avg_views": 25000,
                "avg_followers_gained": 130,
                "avg_shares": 380,
                "avg_follower_conversion_rate": 0.01,
                "avg_engagement_rate": 0.08,
                "avg_completion_rate": 0.6,
            },
            {
                "group_key": "meme_edit",
                "posts": 2,
                "avg_views": 52000,
                "avg_followers_gained": 35,
                "avg_shares": 1500,
                "avg_follower_conversion_rate": 0.002,
                "avg_engagement_rate": 0.03,
                "avg_completion_rate": 0.2,
            },
        ],
    }

    insights = generate_grouped_insights(grouped)
    recommendations = generate_recommendations(grouped)
    goal_groups = build_goal_recommendation_groups(grouped)

    assert any("prioritize 'recruiting'" in item["summary"] for item in insights)
    assert any(rec["action"] == "increase" and rec["focus"] == "recruiting" for rec in recommendations)
    assert any(rec["action"] == "decrease" and rec["focus"] == "funny_clips" for rec in recommendations)
    assert goal_groups["views"]["topic_type"]["best"]["group_key"] == "funny_clips"
    assert goal_groups["followers"]["hook_type"]["best"]["group_key"] == "stat_shock"
    assert goal_groups["shares"]["video_style"]["best"]["group_key"] == "meme_edit"
