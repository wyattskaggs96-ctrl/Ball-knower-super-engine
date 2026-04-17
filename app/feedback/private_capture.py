from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.sources.private_intel_source import PrivateIntelItem

DEFAULT_CAPTURE_INPUT_PATH = Path("data/private_capture_template.json")
DEFAULT_PRIVATE_INTEL_PATH = Path("data/private_intel.json")


def _split_tags(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]

    text = str(raw or "").strip()
    if not text:
        return []

    separators = ["|", ","]
    tokens = [text]
    for separator in separators:
        next_tokens: list[str] = []
        for token in tokens:
            next_tokens.extend(token.split(separator))
        tokens = next_tokens

    return [token.strip() for token in tokens if token.strip()]


def _build_summary(payload: dict[str, Any]) -> str:
    selected_text = str(payload.get("selected_text", "")).strip()
    quick_summary = str(payload.get("quick_summary", "")).strip()

    if selected_text and quick_summary:
        return f"{quick_summary}\n\nCaptured quote: {selected_text}"
    if selected_text:
        return selected_text
    return quick_summary


def capture_to_private_item(payload: dict[str, Any]) -> dict[str, Any]:
    page_title = str(payload.get("page_title", "")).strip()
    selected_text = str(payload.get("selected_text", "")).strip()
    title = page_title or (selected_text[:120] if selected_text else "Private intel capture")

    item = {
        "source": str(payload.get("source", "Manual private capture")).strip() or "Manual private capture",
        "article_url": str(payload.get("url", "")).strip() or None,
        "title": title,
        "summary": _build_summary(payload),
        "team_tags": _split_tags(payload.get("team_tags")),
        "player_tags": _split_tags(payload.get("player_tags")),
        "urgency": str(payload.get("urgency", "medium")).strip() or "medium",
        "confidence": payload.get("confidence", "medium"),
        "note_type": str(payload.get("note_type", "other")).strip() or "other",
    }

    return PrivateIntelItem.model_validate(item).model_dump(mode="json")


def load_capture_entries(path: str | Path) -> list[dict[str, Any]]:
    payload: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict):
        return [dict(payload)]
    raise ValueError("Capture input must be a JSON object or list of objects")


def append_private_intel(entries: list[dict[str, Any]], private_intel_path: str | Path) -> int:
    target = Path(private_intel_path)
    existing: list[dict[str, Any]] = []
    if target.exists():
        current = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(current, list):
            raise ValueError("private_intel target must be a JSON list")
        existing = [dict(item) for item in current]

    existing.extend(entries)
    target.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return len(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert local private capture entries into private_intel items")
    parser.add_argument("--input", default=str(DEFAULT_CAPTURE_INPUT_PATH), help="Capture JSON file (object or list)")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_PRIVATE_INTEL_PATH),
        help="Destination private intel JSON list",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print normalized private_intel items instead of writing output",
    )
    args = parser.parse_args()

    captures = load_capture_entries(args.input)
    normalized = [capture_to_private_item(entry) for entry in captures]

    if args.print_only:
        print(json.dumps(normalized, indent=2))
        return

    appended_count = append_private_intel(normalized, args.output)
    print(f"Appended {appended_count} private intel item(s) to {args.output}")


if __name__ == "__main__":
    main()
