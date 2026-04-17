# Label Validation Guide

Use this before importing manual analytics or private intel to prevent bad labels from entering the engine.

## Run validation

```bash
python main.py validate-labels
```

Optional scopes:

```bash
python main.py validate-labels --scope manual
python main.py validate-labels --scope private
```

Optional file overrides:

```bash
python main.py validate-labels --manual-file data/manual_tiktok_analytics.csv --private-file data/private_intel.json
```

## What gets checked

- `data/manual_tiktok_analytics.csv`
  - `topic_type`
  - `hook_type`
  - `video_style`
- `data/private_intel.json`
  - `note_type`
  - `urgency`
  - `confidence`

## Confidence rules

`confidence` accepts:

- `low`, `medium`, `high`
- numeric value from `0` to `1` (for example `0.42` or `1`)

## When validation fails

The CLI prints each invalid row/item with:

- file context (`manual analytics row N` or `private intel item N`)
- field name
- invalid value
- allowed values

Fix the listed labels and rerun until you see:

`Label validation passed: all checked labels are valid.`
