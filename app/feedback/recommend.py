from __future__ import annotations


def generate_recommendations(grouped_performance: dict[str, list[dict]]) -> list[dict[str, str]]:
    recommendations: list[dict[str, str]] = []

    mapping = {
        "topic_performance": "topic scoring",
        "hook_performance": "hook recommendations",
        "timing_performance": "posting recommendations",
        "length_performance": "content planning",
        "video_style_performance": "content planning",
    }

    for performance_key, engine_target in mapping.items():
        rows = grouped_performance.get(performance_key, [])
        if not rows:
            continue
        best = rows[0]
        worst = rows[-1]

        recommendations.append(
            {
                "engine_target": engine_target,
                "action": "increase",
                "focus": str(best["group_key"]),
                "reason": (
                    f"Best {performance_key} by follower conversion "
                    f"({best['avg_follower_conversion_rate']:.4f}) and engagement ({best['avg_engagement_rate']:.4f})."
                ),
            }
        )

        if worst["group_key"] != best["group_key"]:
            recommendations.append(
                {
                    "engine_target": engine_target,
                    "action": "decrease",
                    "focus": str(worst["group_key"]),
                    "reason": (
                        f"Lowest {performance_key} by follower conversion "
                        f"({worst['avg_follower_conversion_rate']:.4f})."
                    ),
                }
            )

    return recommendations
