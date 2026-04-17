from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app.core.label_config import MANUAL_ANALYTICS_LABELS, PRIVATE_INTEL_LABELS


def _normalize_label(value: Any) -> str:
    return str(value or "").strip().lower()


def validate_manual_analytics_labels(path: str | Path) -> list[str]:
    errors: list[str] = []
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        for row_idx, row in enumerate(csv.DictReader(f), start=2):
            for field, allowed in MANUAL_ANALYTICS_LABELS.items():
                value = _normalize_label(row.get(field, ""))
                if value and value not in allowed:
                    errors.append(
                        f"manual analytics row {row_idx}: field '{field}' has invalid value '{value}'. "
                        f"Allowed: {sorted(allowed)}"
                    )
    return errors


def _validate_confidence_value(value: Any) -> bool:
    if isinstance(value, (int, float)):
        numeric = float(value)
        return 0.0 <= numeric <= 1.0

    text = _normalize_label(value)
    if text in PRIVATE_INTEL_LABELS["confidence"]:
        return True
    try:
        numeric = float(text)
    except ValueError:
        return False
    return 0.0 <= numeric <= 1.0


def validate_private_intel_labels(path: str | Path) -> list[str]:
    errors: list[str] = []
    payload: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return ["private intel: file must contain a JSON list of items"]

    for idx, item in enumerate(payload, start=1):
        note_type = _normalize_label(item.get("note_type", ""))
        if note_type and note_type not in PRIVATE_INTEL_LABELS["note_type"]:
            errors.append(
                f"private intel item {idx}: field 'note_type' has invalid value '{note_type}'. "
                f"Allowed: {sorted(PRIVATE_INTEL_LABELS['note_type'])}"
            )

        urgency = _normalize_label(item.get("urgency", ""))
        if urgency and urgency not in PRIVATE_INTEL_LABELS["urgency"]:
            errors.append(
                f"private intel item {idx}: field 'urgency' has invalid value '{urgency}'. "
                f"Allowed: {sorted(PRIVATE_INTEL_LABELS['urgency'])}"
            )

        confidence = item.get("confidence", "")
        if confidence != "" and not _validate_confidence_value(confidence):
            errors.append(
                f"private intel item {idx}: field 'confidence' has invalid value '{confidence}'. "
                "Allowed: ['low', 'medium', 'high'] or numeric values from 0 to 1"
            )

    return errors


def validate_all_labels(
    manual_path: str | Path = "data/manual_tiktok_analytics.csv",
    private_path: str | Path = "data/private_intel.json",
) -> dict[str, list[str]]:
    return {
        "manual": validate_manual_analytics_labels(manual_path),
        "private": validate_private_intel_labels(private_path),
    }
