from __future__ import annotations

import argparse
from pathlib import Path

from app.agents.content_scorer import ContentScoringAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.script_generator import ScriptGeneratorAgent
from app.agents.trend_scout import TrendScoutAgent
from app.core.config import Settings
from app.core.llm import LLMClient
from app.db.database import get_connection, init_db
from app.db.repository import Repository
from app.feedback.engine_integration import feedback_report, run_feedback_loop
from app.pipelines.run_daily_pipeline import run_daily_pipeline
from app.pipelines.simulate_daily_sheet import simulate_daily_content_sheet
from app.services.content_service import ContentService
from app.services.export_service import ExportService
from app.services.trend_service import TrendService


def build_container() -> tuple[Settings, Repository, TrendService, ContentService, ExportService]:
    settings = Settings.from_env()
    settings.ensure_directories()

    conn = get_connection(settings.db_path)
    init_db(conn, str(Path(__file__).parent / "db" / "schema.sql"))

    repo = Repository(conn)
    llm = LLMClient(settings)

    trend_service = TrendService(TrendScoutAgent(repo), settings)
    content_service = ContentService(
        scorer=ContentScoringAgent(repo, llm),
        hook_generator=HookGeneratorAgent(repo, llm),
        script_generator=ScriptGeneratorAgent(repo, llm),
    )
    export_service = ExportService(repo, settings.export_dir)

    return settings, repo, trend_service, content_service, export_service


def parse_id_list(raw: str | None) -> list[int] | None:
    if not raw:
        return None
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ball Knower Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scout", help="Ingest and store trend candidates")
    sub.add_parser("score", help="Score trends and recommend top topics")

    hooks_p = sub.add_parser("hooks", help="Generate hooks for a trend")
    hooks_p.add_argument("trend_id", type=int)
    hooks_p.add_argument("--count", type=int, default=4)

    script_p = sub.add_parser("script", help="Generate a content pack from hook")
    script_p.add_argument("hook_id", type=int)

    sub.add_parser("run-daily", help="Run full daily pipeline")
    sub.add_parser("simulate-daily", help="Simulate and export a creator-ready daily content sheet")
    sub.add_parser("feedback-run", help="Run feedback loop agent from mock post-performance data")
    sub.add_parser("feedback-report", help="Read latest generated weekly feedback report")

    export_p = sub.add_parser("export", help="Export content packs")
    export_p.add_argument("--format", choices=["json", "markdown", "both"], default="both")
    export_p.add_argument("--ids", type=str, default=None, help="comma-separated content pack IDs")

    args = parser.parse_args()

    settings, repo, trend_service, content_service, export_service = build_container()

    if args.command == "scout":
        inserted = trend_service.scout_trends()
        print(f"Inserted {len(inserted)} trend candidates")
    elif args.command == "score":
        recs = content_service.score(settings.score_threshold)
        print(f"Recommended {len(recs)} topics above {settings.score_threshold}")
    elif args.command == "hooks":
        hooks = content_service.generate_hooks(args.trend_id, args.count)
        print(f"Generated {len(hooks)} hooks for trend {args.trend_id}")
        for hook in hooks:
            print(f"- [{hook.id}] {hook.hook_text}")
    elif args.command == "script":
        pack = content_service.generate_script(args.hook_id)
        if not pack:
            print("No content pack generated. Check hook ID.")
        else:
            print(f"Created content pack {pack.id} from hook {args.hook_id}")
    elif args.command == "run-daily":
        result = run_daily_pipeline(trend_service, content_service, settings.score_threshold)
        print(result)
    elif args.command == "simulate-daily":
        result = simulate_daily_content_sheet()
        print(result)
    elif args.command == "feedback-run":
        result = run_feedback_loop(repo, settings.export_dir)
        print(result)
    elif args.command == "feedback-report":
        print(feedback_report(settings.export_dir))
    elif args.command == "export":
        ids = parse_id_list(args.ids)
        if args.format in {"json", "both"}:
            print(f"JSON export: {export_service.export_json(ids=ids)}")
        if args.format in {"markdown", "both"}:
            print(f"Markdown export: {export_service.export_markdown(ids=ids)}")


if __name__ == "__main__":
    main()
