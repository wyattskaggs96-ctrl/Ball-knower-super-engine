from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MANUAL_CSV_PATH = Path("data/manual_tiktok_analytics.csv")
OPTIONAL_NUMERIC_FIELDS = {
    "likes",
    "comments",
    "shares",
    "saves",
    "profile_views",
    "followers_gained",
    "watch_time_seconds",
    "completion_rate",
}
REQUIRED_FIELDS = {
    "post_id",
    "post_timestamp",
    "topic_type",
    "hook_type",
    "video_style",
    "length_seconds",
    "views",
}


@dataclass
class ManualImportResult:
    records: list[dict[str, Any]]
    errors: list[str]


def _split_tag_field(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw or "").strip()
    if not text:
        return []
    return [part.strip() for part in text.split("|") if part.strip()]


def _read_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Manual analytics JSON must be a list of objects")
        return [dict(item) for item in payload]

    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def load_manual_posts(path: str | Path = DEFAULT_MANUAL_CSV_PATH) -> ManualImportResult:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Manual analytics file not found: {target}")

    rows = _read_records(target)
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []

    for idx, row in enumerate(rows, start=2):
        missing = sorted(name for name in REQUIRED_FIELDS if not str(row.get(name, "")).strip())
        if missing:
            errors.append(f"row {idx}: missing required fields: {', '.join(missing)}")
            continue

        try:
            item: dict[str, Any] = {
                "post_id": str(row.get("post_id", "")).strip(),
                "post_url": str(row.get("post_url", "")).strip(),
                "post_timestamp": str(row.get("post_timestamp", "")).strip(),
                "topic_type": str(row.get("topic_type", "unknown")).strip() or "unknown",
                "hook_type": str(row.get("hook_type", "unknown")).strip() or "unknown",
                "video_style": str(row.get("video_style", "unknown")).strip() or "unknown",
                "teams_tagged": _split_tag_field(row.get("teams_tagged")),
                "players_tagged": _split_tag_field(row.get("players_tagged")),
                "length_seconds": float(row.get("length_seconds", 0) or 0),
                "views": float(row.get("views", 0) or 0),
            }
            for field in OPTIONAL_NUMERIC_FIELDS:
                item[field] = float(row.get(field, 0) or 0)
            normalized.append(item)
        except (TypeError, ValueError) as exc:
            errors.append(f"row {idx}: invalid values ({exc})")

    return ManualImportResult(records=normalized, errors=errors)
