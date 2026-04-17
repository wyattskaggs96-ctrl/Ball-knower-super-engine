from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.models import TrendCandidate


def _confidence_to_float(value: str | float | int | None) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    mapping = {"low": 0.45, "medium": 0.65, "high": 0.85}
    return mapping.get(str(value or "").lower(), 0.55)


def infer_topic_lane(trend: TrendCandidate) -> str:
    text = f"{trend.topic} {trend.summary} {trend.sport}".lower()
    if any(term in text for term in ["transfer portal", "portal", "tampering"]):
        return "transfer_portal"
    if any(term in text for term in ["recruit", "decommit", "five-star", "commitment", "nil"]):
        return "recruiting"
    if any(term in text for term in ["draft", "trade", "finals", "playoff", "schedule", "mvp", "championship"]):
        return "mainstream"
    return "general"


@dataclass
class WeightingContext:
    trend_source_counts: dict[str, dict[str, int]]
    high_urgency_sources: set[str]
    private_intel_counts: dict[str, int]
    private_intel_confidence: dict[str, float]
    feedback_best_topic_by_goal: dict[str, str]
    feedback_weak_topic_by_goal: dict[str, str]


def build_weighting_context(
    trend_source_report_path: str | Path = "data/exports/trend_source_report.json",
    private_intel_path: str | Path = "data/private_intel.json",
    feedback_path: str | Path = "data/exports/engine_recommendations.json",
) -> WeightingContext:
    trend_payload = json.loads(Path(trend_source_report_path).read_text(encoding="utf-8"))
    trend_source_counts: dict[str, dict[str, int]] = {}
    high_urgency_sources: set[str] = set()

    for item in trend_payload.get("high_urgency_items", []):
        high_urgency_sources.add(item.get("source", ""))

    for source, rows in trend_payload.get("top_trends_by_source", {}).items():
        lane_counts = {
            "recruiting": 0,
            "transfer_portal": 0,
            "mainstream": 0,
            "general": 0,
        }
        for row in rows:
            topic_type = row.get("topic_type", "general")
            if topic_type in {"recruiting", "transfer_portal"}:
                lane_counts[topic_type] += 1
            elif topic_type in {"championship", "breaking_news", "general"}:
                lane_counts["mainstream"] += 1
            else:
                lane_counts["general"] += 1
        trend_source_counts[source] = lane_counts

    private_rows = json.loads(Path(private_intel_path).read_text(encoding="utf-8"))
    private_intel_counts = {"recruiting": 0, "transfer_portal": 0, "general": 0}
    private_intel_confidence = {"recruiting": 0.0, "transfer_portal": 0.0, "general": 0.0}
    for row in private_rows:
        lane = row.get("note_type", "general")
        if lane not in private_intel_counts:
            lane = "general"
        private_intel_counts[lane] += 1
        private_intel_confidence[lane] += _confidence_to_float(row.get("confidence"))

    for lane, count in private_intel_counts.items():
        if count:
            private_intel_confidence[lane] = round(private_intel_confidence[lane] / count, 3)

    feedback_payload = json.loads(Path(feedback_path).read_text(encoding="utf-8"))
    goal_groups = feedback_payload.get("goal_aware_recommendations", {})
    feedback_best_topic_by_goal: dict[str, str] = {}
    feedback_weak_topic_by_goal: dict[str, str] = {}
    for goal in ("views", "followers", "shares"):
        topic_group = goal_groups.get(goal, {}).get("topic_type", {})
        feedback_best_topic_by_goal[goal] = topic_group.get("best", {}).get("group_key", "")
        feedback_weak_topic_by_goal[goal] = topic_group.get("weakest", {}).get("group_key", "")

    return WeightingContext(
        trend_source_counts=trend_source_counts,
        high_urgency_sources=high_urgency_sources,
        private_intel_counts=private_intel_counts,
        private_intel_confidence=private_intel_confidence,
        feedback_best_topic_by_goal=feedback_best_topic_by_goal,
        feedback_weak_topic_by_goal=feedback_weak_topic_by_goal,
    )


def apply_source_weighting(trend: TrendCandidate, scores: dict, context: WeightingContext) -> dict:
    lane = infer_topic_lane(trend)
    source_weight = 1.0
    source_signals: list[str] = []

    is_recruiting_lane = lane in {"recruiting", "transfer_portal"}
    has_public_mainstream_signal = False
    if is_recruiting_lane and context.private_intel_counts.get(lane, 0) > 0:
        source_weight += 0.2
        source_signals.append("private_intel")

    mainstream_hits = 0
    for source in ("espn", "bleacher_report"):
        mainstream_hits += int(context.trend_source_counts.get(source, {}).get("mainstream", 0) > 0)
    if lane == "mainstream" and mainstream_hits > 0:
        source_weight += 0.1 * mainstream_hits
        has_public_mainstream_signal = True
        source_signals.append("espn_bleacher_public")

    if is_recruiting_lane and context.trend_source_counts.get("on3", {}).get(lane, 0) > 0:
        source_weight += 0.12
        source_signals.append("on3_context")

    urgency_weight = 1.0
    if "x_watchlist" in context.high_urgency_sources:
        urgency_weight += 0.08
        source_signals.append("x_watchlist_velocity")

    def goal_fit_weight(goal: str) -> float:
        fit = 1.0
        best = context.feedback_best_topic_by_goal.get(goal, "")
        weak = context.feedback_weak_topic_by_goal.get(goal, "")
        if best and (best == lane or (best == "recruiting" and is_recruiting_lane)):
            fit += 0.06
            source_signals.append(f"feedback_best_{goal}")
        if weak and weak == lane:
            fit -= 0.03
        return fit

    view_goal_weight = 1.0
    if has_public_mainstream_signal:
        view_goal_weight += 0.14
    if lane == "mainstream":
        view_goal_weight += 0.06

    follow_goal_weight = 1.0 + (
        (scores["pov_strength_score"] + scores["clarity_1s_score"] + scores["fan_identity_score"]) / 300.0 - 0.55
    ) * 0.22

    share_goal_weight = 1.0 + (
        (scores["sendability_score"] + scores["rivalry_score"] + scores["emotion_score"]) / 300.0 - 0.55
    ) * 0.24

    view_fit = goal_fit_weight("views")
    follow_fit = goal_fit_weight("followers")
    share_fit = goal_fit_weight("shares")
    account_fit_weight = round((view_fit + follow_fit + share_fit) / 3, 3)

    weighted_view_score = round(scores["view_score"] * source_weight * urgency_weight * view_fit * view_goal_weight, 2)
    weighted_follow_score = round(scores["follow_score"] * source_weight * follow_fit * follow_goal_weight, 2)
    weighted_share_score = round(scores["share_score"] * source_weight * urgency_weight * share_fit * share_goal_weight, 2)

    weighted_goal = max(
        [("views", weighted_view_score), ("followers", weighted_follow_score), ("shares", weighted_share_score)],
        key=lambda item: item[1],
    )
    primary_goal = weighted_goal[0]

    goal_bias = {
        "views": 1.0,
        "followers": 1.01,
        "shares": 1.02,
    }
    final_goal_weight = goal_bias[primary_goal]

    weighted_total = round(weighted_goal[1] * final_goal_weight, 2)

    return {
        "source_weight": round(source_weight, 3),
        "account_fit_weight": round(account_fit_weight, 3),
        "urgency_weight": round(urgency_weight, 3),
        "final_goal_weight": round(final_goal_weight, 3),
        "weighted_view_score": weighted_view_score,
        "weighted_follow_score": weighted_follow_score,
        "weighted_share_score": weighted_share_score,
        "weighted_primary_goal": primary_goal,
        "weighted_goal_score": round(weighted_goal[1], 2),
        "weighted_total_score": weighted_total,
        "topic_lane": lane,
        "source_signals": sorted(set(source_signals)),
        "is_public_trend_story": lane == "mainstream" or "espn_bleacher_public" in source_signals,
        "is_premium_intel_story": "private_intel" in source_signals,
    }
