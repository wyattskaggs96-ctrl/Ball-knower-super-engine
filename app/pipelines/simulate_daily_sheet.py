from __future__ import annotations

import json
from pathlib import Path

from app.core.models import ContentPack, TrendCandidate
from app.core.scoring import ScoringEngine
from app.sources import manual_source


def _hooks_for_topic(topic: str) -> list[str]:
    t = topic.strip().rstrip("?.!")
    return [
        f"Nobody is talking about this: {t.lower()} is the real fault line.",
        f"This just changed everything for {t.lower()}.",
        f"Fans are missing what this actually means for {t.lower()}.",
        f"Pick a side: {t.lower()} is genius strategy or panic mode.",
        f"I promise this {t.lower()} take will make somebody mad in 10 seconds.",
    ]


def _pick_hook(hooks: list[str], score: float) -> str:
    if score >= 86:
        return hooks[0]
    if score >= 82:
        return hooks[1]
    return hooks[2]


def _score_reasoning(topic: TrendCandidate, score_breakdown: dict) -> str:
    sport = topic.sport
    return (
        f"High upside for debate in {sport}. "
        f"Virality={score_breakdown['virality']}, Controversy={score_breakdown['controversy']}, "
        f"Recognition={score_breakdown['recognition']}. "
        "Topic has clear opposing sides and can be explained fast with one stat + one clip."
    )


def _build_pack(topic: TrendCandidate, selected_hook: str, idx: int) -> ContentPack:
    return ContentPack(
        id=idx,
        trend_candidate_id=idx,
        hook_id=idx,
        overlay_lines=[
            "BALL KNOWER EMERGENCY MEETING 🚨",
            selected_hook,
            "This is bigger than one headline.",
            "Pick a side before the comments explode.",
        ],
        caption=(
            f"{selected_hook} If this sounds harsh, good. "
            "Sports conversations got too soft and this topic proves it. "
            "#ballknower #sportstok #debate"
        ),
        cta="Drop your side in one sentence: AGREE or DISAGREE. No fence-sitting.",
        creator_notes=(
            f"Footage plan for {topic.sport}: open with 1 face-cam hot take (0-2s), "
            "cut to stat graphic (2-6s), insert game/recruiting/press clip (6-14s), "
            "end on creator reaction with on-screen poll."
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
                "suggested_visual": "Tight face-cam opener with bold text pop-in",
                "editing_style_notes": "0.2s zoom punch + whoosh SFX + subtitle emphasis",
            },
            {
                "scene": 2,
                "timing_seconds": [2, 6],
                "line": overlay_lines[2],
                "suggested_visual": "Stat card or headline screenshot supporting the take",
                "editing_style_notes": "Fast cut with light shake transition and highlighted keywords",
            },
            {
                "scene": 3,
                "timing_seconds": [6, 12],
                "line": row["score_reasoning"],
                "suggested_visual": "Game clip / press clip / recruiting clip tied to argument",
                "editing_style_notes": "2-3 jump cuts, captions kept under 7 words per beat",
            },
            {
                "scene": 4,
                "timing_seconds": [12, 18],
                "line": row["content_pack"]["cta"],
                "suggested_visual": "Creator reaction + comment bait poll overlay",
                "editing_style_notes": "Hard stop music hit at second 15, lingering CTA text to second 18",
            },
        ]

        blueprint.append(
            {
                "content_pack_rank": idx,
                "topic": row["topic"],
                "best_hook": selected_hook,
                "target_duration_seconds": 18,
                "pacing_profile": "TikTok fast-cut / high-retention / first-2-second hook",
                "music_style_suggestion": "Aggressive trap-sports beat at 140-150 BPM with bass drops",
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


def _render_daily_post_ready(rows: list[dict]) -> str:
    lines = ["# Ball Knower Daily Post-Ready Sheet", ""]

    for row in rows:
        lines.extend(
            [
                "----------------------------------------",
                f"TOPIC: {row['topic']}",
                "",
                f"POSTABILITY SCORE: {round(row['score'])}",
                "",
                "HOOK OPTIONS:",
            ]
        )
        for idx, hook in enumerate(row["hooks"][:3], start=1):
            lines.append(f"{idx}. {hook}")

        overlay_lines = row["content_pack"]["overlay_lines"][:3]
        lines.extend(
            [
                "",
                "SELECTED HOOK:",
                "",
                "OVERLAY (EDITABLE):",
                *(f"- {line}" for line in overlay_lines),
                "",
                "CAPTION:",
                row["content_pack"]["caption"],
                "",
                "CTA:",
                row["content_pack"]["cta"],
                "",
                "NOTES:",
                f"- {row['content_pack']['creator_notes']}",
                "- Add one reaction clip that supports your strongest claim.",
                "- Add one quick stat overlay card before the CTA.",
                "----------------------------------------",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _render_top_5_post_now(rows: list[dict]) -> str:
    lines = ["# Top 5 Post Now", ""]
    for idx, row in enumerate(rows[:5], start=1):
        lines.append(f"{idx}. {row['topic']} (Postability: {round(row['score'])})")
    return "\n".join(lines) + "\n"


def simulate_daily_content_sheet(output_path: str = "data/exports/example_output.md") -> dict:
    trends = manual_source.fetch_trends()
    scoring = ScoringEngine()

    ranked: list[tuple[TrendCandidate, dict]] = []
    for trend in trends:
        scored = scoring.score(trend)
        ranked.append((trend, scored))

    ranked.sort(key=lambda item: item[1]["total_score"], reverse=True)
    top = ranked[:10]

    rows: list[dict] = []
    for idx, (trend, scored) in enumerate(top, start=1):
        hooks = _hooks_for_topic(trend.topic)
        selected_hook = _pick_hook(hooks, scored["total_score"])
        content_pack = _build_pack(trend, selected_hook, idx)

        rows.append(
            {
                "topic": trend.topic,
                "score": scored["total_score"],
                "score_reasoning": _score_reasoning(trend, scored),
                "hooks": hooks[:5],
                "selected_hook": selected_hook,
                "content_pack": content_pack.model_dump(mode="json"),
            }
        )

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

    top_5_post_now_path = out_path.parent / "top_5_post_now.md"
    top_5_post_now_path.write_text(_render_top_5_post_now(rows), encoding="utf-8")

    return {
        "top_topics": len(rows),
        "markdown_output": str(out_path),
        "json_output": str(json_path),
        "video_blueprint_output": str(blueprint_path),
        "daily_post_ready_output": str(daily_post_ready_path),
        "top_5_post_now_output": str(top_5_post_now_path),
    }
