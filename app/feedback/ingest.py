from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.feedback.manual_intake import DEFAULT_MANUAL_CSV_PATH, ManualImportResult, load_manual_posts


DEFAULT_MOCK_PATH = Path("data/mock_tiktok_posts.json")


def load_mock_posts(path: str | Path = DEFAULT_MOCK_PATH) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError("Mock TikTok data must be a list of posts")
    return payload


def load_posts_by_source(source: str, manual_file: str | Path = DEFAULT_MANUAL_CSV_PATH) -> tuple[list[dict[str, Any]], list[str]]:
    source_key = source.lower()
    if source_key == "mock":
        return load_mock_posts(), []
    if source_key == "manual":
        result = load_manual_posts(manual_file)
        return result.records, result.errors
    if source_key == "all":
        manual_result: ManualImportResult = load_manual_posts(manual_file)
        return load_mock_posts() + manual_result.records, manual_result.errors
    raise ValueError("source must be one of: mock, manual, all")
