from __future__ import annotations


def _pick(rows: list[dict]) -> tuple[dict | None, dict | None]:
    if not rows:
        return None, None
    return rows[0], rows[-1]


def generate_grouped_insights(grouped_performance: dict[str, list[dict]]) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    for insight_type, rows in grouped_performance.items():
        top_row, bottom_row = _pick(rows)
        if not top_row:
            continue
        insights.append(
            {
                "insight_type": insight_type,
                "insight_key": str(top_row["group_key"]),
                "direction": "up",
                "summary": f"{insight_type}: prioritize '{top_row['group_key']}' (conversion {top_row['avg_follower_conversion_rate']:.4f}).",
            }
        )
        if bottom_row and bottom_row["group_key"] != top_row["group_key"]:
            insights.append(
                {
                    "insight_type": insight_type,
                    "insight_key": str(bottom_row["group_key"]),
                    "direction": "down",
                    "summary": f"{insight_type}: deprioritize '{bottom_row['group_key']}' (conversion {bottom_row['avg_follower_conversion_rate']:.4f}).",
                }
            )
    return insights
