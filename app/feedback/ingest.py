from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MOCK_PATH = Path("data/mock_tiktok_posts.json")


def load_mock_posts(path: str | Path = DEFAULT_MOCK_PATH) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError("Mock TikTok data must be a list of posts")
    return payload
