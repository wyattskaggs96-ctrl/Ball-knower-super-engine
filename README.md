# Ball Knower Engine (V1)

Ball Knower Engine is a modular, CLI-first Python project for AI-powered sports content ideation.

## What V1 does

1. Ingests trending sports topics from simple adapters (RSS, Reddit, manual).
2. Scores trends with a weighted rubric.
3. Generates TikTok-style hooks for recommended topics.
4. Generates a final content pack (overlay lines, caption, CTA, creator notes).
5. Stores pipeline outputs in SQLite.
6. Exports content packs to JSON and Markdown.

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

### Export content packs
```bash
python main.py export --format both
python main.py export --format json --ids 1,2
```

## Config

All config is environment-variable based. See `.env.example`.

## Notes

- LLM is centralized in `app/core/llm.py` with mock behavior by default.
- Source adapters are mock-first and ready for real integrations.
- DB schema is in `app/db/schema.sql`.
- Repo layer is in `app/db/repository.py`.

## Testing

```bash
pytest -q
```
