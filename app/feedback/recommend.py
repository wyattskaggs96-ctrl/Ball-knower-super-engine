from __future__ import annotations


GOAL_METRICS = {
    "views": "avg_views",
    "followers": "avg_followers_gained",
    "shares": "avg_shares",
}


def _rows_for_goal(rows: list[dict], goal: str) -> list[dict]:
    metric = GOAL_METRICS[goal]
    return sorted(rows, key=lambda row: float(row.get(metric, 0.0)), reverse=True)


def build_goal_recommendation_groups(grouped_performance: dict[str, list[dict]]) -> dict[str, dict[str, dict[str, dict]]]:
    dimension_keys = {
        "topic_type": "topic_performance",
        "hook_type": "hook_performance",
        "video_style": "video_style_performance",
    }

    grouped: dict[str, dict[str, dict[str, dict]]] = {}
    for goal in GOAL_METRICS:
        grouped[goal] = {}
        for dimension_name, performance_key in dimension_keys.items():
            rows = _rows_for_goal(grouped_performance.get(performance_key, []), goal)
            if not rows:
                continue
            grouped[goal][dimension_name] = {"best": rows[0], "weakest": rows[-1]}
    return grouped


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

    goal_groups = build_goal_recommendation_groups(grouped_performance)
    for goal, dimensions in goal_groups.items():
        for dimension_name, group in dimensions.items():
            best = group["best"]
            weakest = group["weakest"]
            metric = GOAL_METRICS[goal]

            recommendations.append(
                {
                    "engine_target": f"{dimension_name} recommendations",
                    "action": "increase",
                    "focus": str(best["group_key"]),
                    "goal": goal,
                    "reason": f"Best {dimension_name} for {goal} ({metric}={best[metric]:.2f}).",
                }
            )

            if weakest["group_key"] != best["group_key"]:
                recommendations.append(
                    {
                        "engine_target": f"{dimension_name} recommendations",
                        "action": "decrease",
                        "focus": str(weakest["group_key"]),
                        "goal": goal,
                        "reason": f"Weakest {dimension_name} for {goal} ({metric}={weakest[metric]:.2f}).",
                    }
                )

    return recommendations
