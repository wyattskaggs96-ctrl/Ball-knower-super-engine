# Ball Knower Engine (V1)

Ball Knower Engine is a modular, CLI-first Python project for aggressive, debate-first sports content ideation.

## What V1 does

1. Ingests trending sports topics from simple adapters (RSS, Reddit, manual).
2. Scores trends with a weighted rubric.
3. Generates TikTok-style hooks for recommended topics.
4. Generates a final content pack (overlay lines, caption, CTA, creator notes).
5. Stores pipeline outputs in SQLite.
6. Exports content packs to JSON and Markdown.
7. Simulates a creator-ready daily content sheet from curated trend data.
8. Generates a scene-by-scene TikTok video blueprint JSON for production handoff.

## Architecture

```
ball-knower-engine/
  app/
    agents/
    core/
    db/
    pipelines/
    sources/
    services/
    cli.py
  data/
    raw/
    processed/
    exports/
    sample_trends.json
  tests/
  .env.example
  requirements.txt
  README.md
  main.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## CLI commands

### Scout trends
```bash
python main.py scout
```

### Score trends
```bash
python main.py score
```

### Generate hooks for a trend
```bash
python main.py hooks 1 --count 4
```

### Generate content pack from a hook
```bash
python main.py script 1
```

### Run end-to-end daily flow
```bash
python main.py run-daily
```

### Simulate daily creator sheet (no external integrations)
```bash
python main.py simulate-daily
```

### Export content packs
```bash
python main.py export --format both
python main.py export --format json --ids 1,2
```

## How to review output quality without running the full system

Use the prebuilt review artifact:
- `data/exports/example_output.md`
- `data/exports/video_blueprint.json`

What to evaluate in this file:
- Top 10 selected topics are ranked by score.
- Each topic includes score reasoning (why this is worth posting now).
- Each topic includes 3-5 hooks in Ball Knower tone.
- A best hook is selected for execution.
- Overlay text is broken into TikTok-style short lines.
- Caption, CTA, and creator footage notes are creator-ready and debate-first.
- Video blueprint includes scene timing, visuals, edit style, and music style suggestions.

This gives product/editor stakeholders a static, reviewable daily sheet even when runtime execution or APIs are unavailable.

## How this maps to real production usage later

Current V1 is intentionally mock-first and simulation-friendly. As integrations are added:
- Replace mock source adapters with real RSS/Reddit/social ingestion.
- Keep the same `TrendCandidate -> TrendScore -> Hook -> ContentPack` flow.
- Route LLM calls through `app/core/llm.py` with real provider backends.
- Keep markdown/json/video-blueprint export formats stable so creator ops workflows do not break.

In other words: the review artifact format already matches the eventual production handoff format.

## Config

All config is environment-variable based. See `.env.example`.

## Notes

- LLM is centralized in `app/core/llm.py` with mock behavior by default.
- Source adapters are mock-first and ready for real integrations.
- Manual source loads `data/sample_trends.json` by default for rich local simulation.
- DB schema is in `app/db/schema.sql`.
- Repo layer is in `app/db/repository.py`.
- Daily sheet example output is at `data/exports/example_output.md`.
- Video blueprint output is at `data/exports/video_blueprint.json`.

## Testing

```bash
pytest -q
```
