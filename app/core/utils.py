from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_topic(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def make_fingerprint(source: str, topic: str) -> str:
    normalized = f"{source}:{normalize_topic(topic)}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
