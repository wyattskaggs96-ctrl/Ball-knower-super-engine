from __future__ import annotations

import json
import logging
import os
import random
from datetime import datetime, timezone
from pathlib import Path

from app.core.models import ContentPack, TrendCandidate
from app.core.scoring import ScoringEngine
from app.core.source_weighting import apply_source_weighting, build_weighting_context
from app.core.utils import normalize_topic
from app.sources import manual_source
from app.sources.live_trend_source import fetch_live_trends



logger = logging.getLogger(__name__)


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _merge_manual_and_live_trends(manual_trends: list[TrendCandidate], live_trends: list[TrendCandidate]) -> tuple[list[TrendCandidate], int]:
    seen_topics = {normalize_topic(trend.topic) for trend in manual_trends}
    merged = list(manual_trends)
    ingested_live_count = 0

    for trend in live_trends:
        normalized_topic = normalize_topic(trend.topic)
        if normalized_topic in seen_topics:
            continue
        seen_topics.add(normalized_topic)
        merged.append(trend)
        ingested_live_count += 1

    return merged, ingested_live_count


def _hooks_for_topic(topic: str) -> list[str]:
    t = topic.strip().rstrip("?.!")
    lower = t.lower()
    return [
        f"Direct challenge: defend {lower} without lazy narratives.",
        f"Unpopular opinion: {lower} is being treated like a solved issue.",
        f"You're wrong if you think {lower} is only about talent.",
        f"Casual fans think {lower} is obvious—real watchers know it's messy.",
        f"Pick a side: {lower} is overrated or underrated right now.",
    ]


def _pick_hook(hooks: list[str], postability_score: float, rng: random.Random) -> str:
    if postability_score >= 84:
        pool = hooks[:3]
    elif postability_score >= 78:
        pool = hooks[1:4]
    else:
        pool = hooks[2:5]
    return rng.choice(pool)


def _score_reasoning(topic: TrendCandidate, score_breakdown: dict) -> str:
    sport = topic.sport
    return (
        f"High upside for debate in {sport}. "
        f"Virality={score_breakdown['virality']}, Controversy={score_breakdown['controversy']}, "
        f"Recognition={score_breakdown['recognition']}. "
        "Topic has clear opposing sides and can be explained fast with one stat + one clip."
    )


def _postability_components(topic: TrendCandidate, score_breakdown: dict) -> dict:
    lower_topic = topic.topic.lower()

    audience_size = 92.0 if any(k in lower_topic for k in ["nba", "nfl", "lakers", "cowboys", "celtics"]) else 78.0
    clip_availability = 90.0 if topic.sport in {"nba", "nfl", "college basketball"} else 75.0
    controversy = score_breakdown["controversy"]
    comment_potential = 93.0 if any(
        k in lower_topic for k in ["debate", "overrated", "underrated", "controvers", "trade", "portal", "decommit"]
    ) else 80.0
    speed_to_post = 90.0 if any(
        k in topic.sport for k in ["nba", "nfl", "college basketball", "recruiting drama"]
    ) else 76.0

    return {
        "audience_size": audience_size,
        "clip_availability": clip_availability,
        "controversy": controversy,
        "comment_potential": comment_potential,
        "speed_to_post": speed_to_post,
    }


def _postability_score(topic: TrendCandidate, score_breakdown: dict) -> tuple[float, dict]:
    components = _postability_components(topic, score_breakdown)
    score = (
        components["audience_size"] * 0.25
        + components["clip_availability"] * 0.2
        + components["controversy"] * 0.2
        + components["comment_potential"] * 0.2
        + components["speed_to_post"] * 0.15
    )
    return round(score, 2), components


def _build_cta(topic: TrendCandidate) -> str:
    return (
        f"If you disagree, prove it in one sentence with receipts—or admit your {topic.sport} take is casual-tier."
    )


def _build_pack(topic: TrendCandidate, selected_hook: str, idx: int) -> ContentPack:
    return ContentPack(
        id=idx,
        trend_candidate_id=idx,
        hook_id=idx,
        overlay_lines=[
            "BALL KNOWER EMERGENCY MEETING 🚨",
            selected_hook,
            "One side is lying to themselves.",
            "Pick your side and defend it.",
        ],
        caption=(
            f"{selected_hook} If this offends you, good. "
            "Most sports takes collapse the second they're challenged. "
            "#ballknower #sportstok #debate"
        ),
        cta=_build_cta(topic),
        creator_notes=(
            f"Footage plan for {topic.sport}: 0-2s face-cam challenge, 2-6s stat card, "
            "6-13s clip montage with hard cuts, 13-18s reaction + pinned-comment bait."
        ),
    )


def _build_video_blueprint(rows: list[dict]) -> list[dict]:
    blueprint: list[dict] = []
    for idx, row in enumerate(rows, start=1):
        selected_hook = row["selected_hook"]
        overlay_lines = row["content_pack"]["overlay_lines"]

        scenes = [
            {
                "scene": 1,
                "timing_seconds": [0, 2],
                "line": selected_hook,
                "suggested_visual": "Tight face-cam opener with subtitle slam",
                "editing_style_notes": "0.2s zoom punch + bass hit + red caption emphasis",
            },
            {
                "scene": 2,
                "timing_seconds": [2, 6],
                "line": overlay_lines[2],
                "suggested_visual": "Stat card + headline screenshot with highlighted keywords",
                "editing_style_notes": "Fast swipe + shake transition; keep text under 7 words",
            },
            {
                "scene": 3,
                "timing_seconds": [6, 13],
                "line": row["score_reasoning"],
                "suggested_visual": "Clip montage (game/recruiting/presser) supporting main argument",
                "editing_style_notes": "3 jump cuts + speed ramps + beat-synced captions",
            },
            {
                "scene": 4,
                "timing_seconds": [13, 18],
                "line": row["content_pack"]["cta"],
                "suggested_visual": "Creator reaction + poll sticker + pinned-comment prompt",
                "editing_style_notes": "Music dip at 15s, forceful CTA hold to final frame",
            },
        ]

        blueprint.append(
            {
                "content_pack_rank": idx,
                "topic": row["topic"],
                "postability_score": row["postability_score"],
                "best_hook": selected_hook,
                "target_duration_seconds": 18,
                "pacing_profile": "TikTok fast-cut / high-retention / confrontation-first opener",
                "music_style_suggestion": "Aggressive trap-sports beat at 140-150 BPM with punchy transitions",
                "scenes": scenes,
            }
        )

    return blueprint


def _render_markdown(rows: list[dict]) -> str:
    lines = [
        "# Ball Knower Daily Content Sheet (Simulated)",
        "",
        "Review artifact generated from curated trends (no runtime APIs required).",
        "",
    ]

    for i, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## {i}. {row['topic']}",
                f"- **Postability score:** {row['postability_score']} (audience={row['postability_components']['audience_size']}, clips={row['postability_components']['clip_availability']}, controversy={row['postability_components']['controversy']}, comments={row['postability_components']['comment_potential']}, speed={row['postability_components']['speed_to_post']})",
                f"- **Score:** {row['score']}",
                f"- **Score reasoning:** {row['score_reasoning']}",
                "- **Hooks (3-5):**",
            ]
        )
        for hook in row["hooks"]:
            lines.append(f"  - {hook}")
        lines.extend(
            [
                f"- **Best hook selected:** {row['selected_hook']}",
                "- **Overlay text (TikTok lines):**",
            ]
        )
        for line in row["content_pack"]["overlay_lines"]:
            lines.append(f"  - {line}")
        lines.extend(
            [
                f"- **Caption:** {row['content_pack']['caption']}",
                f"- **CTA:** {row['content_pack']['cta']}",
                f"- **Creator notes (footage plan):** {row['content_pack']['creator_notes']}",
                "",
            ]
        )

    return "\n".join(lines)


def _angle_options(topic: str, sport: str) -> list[str]:
    topic_clean = topic.strip().rstrip("?.!")
    lower = topic_clean.lower()

    if "trade" in lower:
        return [
            "Star move vs depth reset",
            "Front office timeline pressure",
            "Why one deal may not fix playoff flaws",
        ]
    if any(k in lower for k in ["draft", "freshman", "portal", "recruit"]):
        return [
            "Hype vs real fit",
            "Roster balance concerns",
            "What matters by midseason",
        ]
    if any(k in lower for k in ["coach", "strategy", "identity"]):
        return [
            "System fit vs talent edge",
            "Identity mismatch warning",
            "Big-picture risk if nothing changes",
        ]

    return [
        f"Big question in {sport}",
        "What the headline misses",
        "One adjustment that changes the outlook",
    ]


def _draft_caption(topic: str) -> str:
    return f"[Draft caption: quick take on {topic.lower()}]"


def _draft_cta() -> str:
    return "[Draft CTA: ask viewers to pick a side in one line]"


def _render_daily_post_ready(rows: list[dict]) -> str:
    sections: list[str] = []
    for row in rows:
        angles = _angle_options(row["topic"], row["sport"])
        notes = [
            f"Footage: pull a recent {row['sport']} clip tied to this topic.",
            "Reaction: use a short creator face-cam response.",
            f"Stat card: one number that supports the {row['topic']} angle.",
        ]
        section = [
            "----------------------------------------",
            f"TOPIC: {row['topic']}",
            "",
            f"POSTABILITY SCORE: {round(row['postability_score'])}",
            "",
            "ANGLE OPTIONS:",
            f"1. {angles[0]}",
            f"2. {angles[1]}",
            f"3. {angles[2]}",
            "",
            "SELECTED HOOK:",
            "",
            "OVERLAY (EDITABLE):",
            "- BALL KNOWER 🚨",
            f"- {row['sport'].upper()} TAKE CHECK",
            "- Add your strongest one-line claim",
            "",
            "CAPTION:",
            _draft_caption(row["topic"]),
            "",
            "CTA:",
            _draft_cta(),
            "",
            "NOTES:",
            f"- {notes[0]}",
            f"- {notes[1]}",
            f"- {notes[2]}",
            "----------------------------------------",
            "",
        ]
        sections.extend(section)

    return "\n".join(sections).rstrip() + "\n"


def _render_top_5_post_now(rows: list[dict]) -> str:
    lines = ["# Top 5 Post Now", "", "Fast picks to post immediately:", ""]
    for idx, row in enumerate(rows[:5], start=1):
        lines.append(f"{idx}. {row['topic']} (Postability {round(row['postability_score'])})")
        lines.append(f"   - Angle: {_angle_options(row['topic'], row['sport'])[0]}")
        lines.append("   - Hook: [write final hook]")
        lines.append("   - CTA: [draft CTA]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_goal_top_3(rows: list[dict], score_key: str, title: str) -> str:
    goal_map = {"view_score": "views", "follow_score": "followers", "share_score": "shares"}
    target_goal = goal_map[score_key]
    primary_first = [row for row in rows if row["primary_goal"] == target_goal]
    fallback = [row for row in rows if row["primary_goal"] != target_goal]
    ranked = sorted(primary_first, key=lambda row: row[score_key], reverse=True)
    if len(ranked) < 3:
        ranked.extend(sorted(fallback, key=lambda row: row[score_key], reverse=True))
    ranked = ranked[:3]

    hook_templates = {
        "views": [
            "This one is exploding right now — quick reset:",
            "If you only watch one sports topic today, make it this:",
            "Fast headline breakdown before everyone runs with bad context:",
        ],
        "followers": [
            "My read on this is simple:",
            "What this actually means for next month:",
            "Ranking this take with full context:",
        ],
        "shares": [
            "Send this to the friend still defending this:",
            "This is pure disrespect and I brought receipts:",
            "Group-chat argument fuel in 15 seconds:",
        ],
    }

    reason_templates = {
        "views": "Broad reach + clear setup + current search heat.",
        "followers": "Strong POV + explanation depth + repeatable Ball Knower angle.",
        "shares": "Rivalry/disrespect energy + high sendability + argument fuel.",
    }

    lines = [title, "", "Top creator-ready topics by goal score:", ""]
    for idx, row in enumerate(ranked, start=1):
        lines.append(f"{idx}. {row['topic']} ({score_key.replace('_', ' ').title()}: {row[score_key]}, Postability: {row['postability_score']})")
        lines.append(f"   - Primary goal: {row['primary_goal']}")
        lines.append(f"   - Suggested hook: {hook_templates[target_goal][idx - 1]} {row['topic']}.")
        lines.append(f"   - Why this fits: {reason_templates[target_goal]}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _top_rows(rows: list[dict], key: str, limit: int = 3, used_topics: set[str] | None = None) -> list[dict]:
    ranked = sorted(rows, key=lambda row: row[key], reverse=True)
    if not used_topics:
        return ranked[:limit]

    picks: list[dict] = []
    delayed: list[dict] = []
    for row in ranked:
        if len(picks) >= limit:
            break
        if row["topic"] in used_topics:
            delayed.append(row)
            continue
        picks.append(row)

    if len(picks) < limit:
        for row in delayed:
            if len(picks) >= limit:
                break
            picks.append(row)
    return picks


def _compact_entry(row: dict, metric: str) -> dict:
    return {
        "topic": row["topic"],
        "sport": row["sport"],
        "topic_lane": row["topic_lane"],
        "metric": metric,
        "metric_score": row[metric],
        "weighted_primary_goal": row["weighted_primary_goal"],
        "source_signals": row["source_signals"],
    }


def _dashboard_payload(rows: list[dict], dashboard_rows: list[dict] | None = None) -> dict:
    def compact(items: list[dict], metric: str) -> list[dict]:
        return [_compact_entry(row, metric) for row in items]

    pool = dashboard_rows or rows
    used_topics: set[str] = set()
    view_rows = _top_rows(rows, "weighted_view_score")
    used_topics.update(row["topic"] for row in view_rows[:2])
    follow_rows = _top_rows(rows, "weighted_follow_score", used_topics=used_topics)
    used_topics.update(row["topic"] for row in follow_rows[:2])
    share_rows = _top_rows(rows, "weighted_share_score", used_topics=used_topics)

    return {
        "best_posts_for_views": compact(view_rows, "weighted_view_score"),
        "best_posts_for_follows": compact(follow_rows, "weighted_follow_score"),
        "best_posts_for_shares": compact(share_rows, "weighted_share_score"),
        "hottest_recruiting_portal_moves": compact(
            _top_rows([row for row in rows if row["topic_lane"] in {"recruiting", "transfer_portal"}], "weighted_total_score"),
            "weighted_total_score",
        ),
        "strongest_public_trend_stories": compact(
            _top_rows([row for row in pool if row["is_public_trend_story"]], "weighted_total_score"),
            "weighted_total_score",
        ),
        "strongest_premium_intel_stories": compact(
            _top_rows([row for row in rows if row["is_premium_intel_story"]], "weighted_total_score"),
            "weighted_total_score",
        ),
        "most_sendable_sports_moments": compact(_top_rows(rows, "sendability_score"), "sendability_score"),
        "stories_with_strongest_account_fit": compact(_top_rows(rows, "account_fit_weight"), "account_fit_weight"),
    }


def _render_goal_dashboard_markdown(payload: dict) -> str:
    sections = [
        ("Best posts for views", payload["best_posts_for_views"], "weighted_view_score"),
        ("Best posts for follows", payload["best_posts_for_follows"], "weighted_follow_score"),
        ("Best posts for shares", payload["best_posts_for_shares"], "weighted_share_score"),
        ("Hottest recruiting/portal moves", payload["hottest_recruiting_portal_moves"], "weighted_total_score"),
        ("Strongest public-trend stories", payload["strongest_public_trend_stories"], "weighted_total_score"),
        ("Strongest premium-intel stories", payload["strongest_premium_intel_stories"], "weighted_total_score"),
        ("Most sendable sports moments", payload["most_sendable_sports_moments"], "sendability_score"),
        ("Stories with strongest account-fit", payload["stories_with_strongest_account_fit"], "account_fit_weight"),
    ]

    lines = ["# Goal Dashboard", "", "Quick picks for daily creator decisions.", ""]
    for title, rows, metric in sections:
        lines.append(f"## {title}")
        if not rows:
            lines.append("- No qualifying stories today.")
            lines.append("")
            continue
        for idx, row in enumerate(rows, start=1):
            lines.append(
                f"- {idx}. {row['topic']} ({metric.replace('_', ' ')}: {row['metric_score']}, lane: {row['topic_lane']}, signals: {', '.join(row['source_signals']) or 'none'})"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def simulate_daily_content_sheet(output_path: str = "data/exports/daily_content_sheet.md") -> dict:
    manual_trends = manual_source.fetch_trends()

    live_enabled = _as_bool(os.getenv("ENABLE_LIVE_TRENDS"), False)
    live_trends = fetch_live_trends() if live_enabled else []
    trends, live_ingested_count = _merge_manual_and_live_trends(manual_trends, live_trends)

    logger.info(
        "Trend pool prepared: manual=%s live_fetched=%s live_ingested=%s total=%s",
        len(manual_trends),
        len(live_trends),
        live_ingested_count,
        len(trends),
    )

    scoring = ScoringEngine()
    weighting_context = build_weighting_context()

    run_seed = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rng = random.Random(run_seed)

    ranked: list[tuple[TrendCandidate, dict, dict, float, dict, float]] = []
    for trend in trends:
        scored = scoring.score(trend)
        weighted = apply_source_weighting(trend, scored, weighting_context)
        postability, components = _postability_score(trend, scored)

        tie_breaker = rng.uniform(-2.5, 2.5)
        final_rank_score = round(weighted["weighted_total_score"] * 0.6 + postability * 0.4 + tie_breaker, 2)

        ranked.append((trend, scored, weighted, postability, components, final_rank_score))

    ranked.sort(key=lambda item: item[5], reverse=True)

    top_pool = ranked[:15] if len(ranked) >= 15 else ranked
    rng.shuffle(top_pool)
    selected_ranked = sorted(top_pool[:10], key=lambda item: item[5], reverse=True)

    all_rows: list[dict] = []
    for idx, (trend, scored, weighted, postability, components, final_rank_score) in enumerate(selected_ranked, start=1):
        hooks = _hooks_for_topic(trend.topic)
        selected_hook = _pick_hook(hooks, postability, rng)
        content_pack = _build_pack(trend, selected_hook, idx)

        all_rows.append(
            {
                "topic": trend.topic,
                "sport": trend.sport,
                "score": scored["total_score"],
                "postability_score": postability,
                "view_score": scored["view_score"],
                "follow_score": scored["follow_score"],
                "share_score": scored["share_score"],
                "sendability_score": scored["sendability_score"],
                "primary_goal": scored["primary_goal"],
                "source_weight": weighted["source_weight"],
                "account_fit_weight": weighted["account_fit_weight"],
                "urgency_weight": weighted["urgency_weight"],
                "final_goal_weight": weighted["final_goal_weight"],
                "weighted_view_score": weighted["weighted_view_score"],
                "weighted_follow_score": weighted["weighted_follow_score"],
                "weighted_share_score": weighted["weighted_share_score"],
                "weighted_primary_goal": weighted["weighted_primary_goal"],
                "weighted_goal_score": weighted["weighted_goal_score"],
                "weighted_total_score": weighted["weighted_total_score"],
                "topic_lane": weighted["topic_lane"],
                "source_signals": weighted["source_signals"],
                "is_public_trend_story": weighted["is_public_trend_story"],
                "is_premium_intel_story": weighted["is_premium_intel_story"],
                "postability_components": components,
                "final_rank_score": final_rank_score,
                "score_reasoning": _score_reasoning(trend, scored),
                "hooks": hooks[:5],
                "selected_hook": selected_hook,
                "content_pack": content_pack.model_dump(mode="json"),
            }
        )

    rows = all_rows[:10]

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_markdown(rows), encoding="utf-8")

    json_path = out_path.with_suffix(".json")
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    video_blueprint = _build_video_blueprint(rows)
    blueprint_path = out_path.parent / "video_blueprint.json"
    blueprint_path.write_text(json.dumps(video_blueprint, indent=2), encoding="utf-8")

    daily_post_ready_path = out_path.parent / "daily_post_ready.md"
    daily_post_ready_path.write_text(_render_daily_post_ready(rows), encoding="utf-8")

    top_5_path = out_path.parent / "top_5_post_now.md"
    top_5_path.write_text(_render_top_5_post_now(rows), encoding="utf-8")

    top_views_path = out_path.parent / "top_3_views.md"
    top_views_path.write_text(_render_goal_top_3(rows, "view_score", "# Top 3 Topics for Views"), encoding="utf-8")

    top_follows_path = out_path.parent / "top_3_follows.md"
    top_follows_path.write_text(_render_goal_top_3(rows, "follow_score", "# Top 3 Topics for Followers"), encoding="utf-8")

    top_shares_path = out_path.parent / "top_3_shares.md"
    top_shares_path.write_text(_render_goal_top_3(rows, "share_score", "# Top 3 Topics for Shares"), encoding="utf-8")

    dashboard_payload = _dashboard_payload(rows, dashboard_rows=all_rows)
    goal_dashboard_json_path = out_path.parent / "goal_dashboard.json"
    goal_dashboard_json_path.write_text(json.dumps(dashboard_payload, indent=2), encoding="utf-8")

    goal_dashboard_md_path = out_path.parent / "goal_dashboard.md"
    goal_dashboard_md_path.write_text(_render_goal_dashboard_markdown(dashboard_payload), encoding="utf-8")

    return {
        "top_topics": len(rows),
        "markdown_output": str(out_path),
        "json_output": str(json_path),
        "video_blueprint_output": str(blueprint_path),
        "daily_post_ready_output": str(daily_post_ready_path),
        "top_5_post_now_output": str(top_5_path),
        "top_3_views_output": str(top_views_path),
        "top_3_follows_output": str(top_follows_path),
        "top_3_shares_output": str(top_shares_path),
        "goal_dashboard_md_output": str(goal_dashboard_md_path),
        "goal_dashboard_json_output": str(goal_dashboard_json_path),
        "run_seed": run_seed,
        "manual_trends_count": len(manual_trends),
        "live_trends_enabled": live_enabled,
        "live_trends_fetched": len(live_trends),
        "live_trends_ingested": live_ingested_count,
        "total_trends_considered": len(trends),
    }
