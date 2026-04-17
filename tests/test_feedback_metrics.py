from app.feedback.metrics import add_post_metrics, build_grouped_performance


def test_add_post_metrics_calculates_rates() -> None:
    posts = [
        {
            "views": 100,
            "likes": 20,
            "comments": 10,
            "shares": 5,
            "saves": 4,
            "followers_gained": 3,
            "completion_rate": 0.5,
            "topic_type": "analysis",
            "hook_type": "stat_shock",
            "posting_window": "evening",
            "length_bucket": "medium",
            "video_style": "facecam_breakdown",
        }
    ]

    enriched = add_post_metrics(posts)

    assert enriched[0]["follower_conversion_rate"] == 0.03
    assert enriched[0]["engagement_rate"] == 0.35
    assert enriched[0]["comment_rate"] == 0.1
    assert enriched[0]["share_rate"] == 0.05
    assert enriched[0]["save_rate"] == 0.04


def test_build_grouped_performance_sorts_best_first() -> None:
    posts = add_post_metrics(
        [
            {
                "views": 100,
                "likes": 20,
                "comments": 10,
                "shares": 10,
                "saves": 4,
                "followers_gained": 5,
                "completion_rate": 0.5,
                "topic_type": "recruiting",
                "hook_type": "stat_shock",
                "posting_window": "evening",
                "length_bucket": "medium",
                "video_style": "facecam_breakdown",
            },
            {
                "views": 100,
                "likes": 10,
                "comments": 3,
                "shares": 2,
                "saves": 1,
                "followers_gained": 1,
                "completion_rate": 0.2,
                "topic_type": "highlights",
                "hook_type": "funny_open",
                "posting_window": "morning",
                "length_bucket": "short",
                "video_style": "meme_edit",
            },
        ]
    )

    grouped = build_grouped_performance(posts)

    assert grouped["topic_performance"][0]["group_key"] == "recruiting"
    assert grouped["topic_performance"][-1]["group_key"] == "highlights"
    assert grouped["topic_performance"][0]["avg_followers_gained"] == 5
    assert grouped["topic_performance"][0]["avg_shares"] == 10
