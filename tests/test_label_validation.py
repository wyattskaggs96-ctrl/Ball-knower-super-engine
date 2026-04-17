from __future__ import annotations

import json

from app.core.validation import validate_manual_analytics_labels, validate_private_intel_labels


def test_manual_label_validation_passes_for_valid_values(tmp_path) -> None:
    sample = tmp_path / "manual.csv"
    sample.write_text(
        "post_id,post_timestamp,topic_type,hook_type,video_style,length_seconds,views\n"
        "row_1,2026-04-15T13:12:00Z,nfl,hot_take,analyst_clip,30,1000\n",
        encoding="utf-8",
    )

    errors = validate_manual_analytics_labels(sample)

    assert errors == []


def test_manual_label_validation_fails_for_invalid_values(tmp_path) -> None:
    sample = tmp_path / "manual.csv"
    sample.write_text(
        "post_id,post_timestamp,topic_type,hook_type,video_style,length_seconds,views\n"
        "row_1,2026-04-15T13:12:00Z,analysis,wild_hook,studio,30,1000\n",
        encoding="utf-8",
    )

    errors = validate_manual_analytics_labels(sample)

    assert len(errors) == 3
    assert "topic_type" in errors[0]
    assert "hook_type" in errors[1]
    assert "video_style" in errors[2]


def test_private_intel_confidence_accepts_string_and_numeric(tmp_path) -> None:
    sample = tmp_path / "private.json"
    sample.write_text(
        json.dumps(
            [
                {"note_type": "recruiting", "urgency": "medium", "confidence": "high"},
                {"note_type": "injury", "urgency": "low", "confidence": 0.4},
                {"note_type": "coaching", "urgency": "high", "confidence": "0.95"},
            ]
        ),
        encoding="utf-8",
    )

    errors = validate_private_intel_labels(sample)

    assert errors == []


def test_private_intel_validation_fails_for_invalid_values(tmp_path) -> None:
    sample = tmp_path / "private.json"
    sample.write_text(
        json.dumps(
            [
                {"note_type": "unknown", "urgency": "now", "confidence": 2},
            ]
        ),
        encoding="utf-8",
    )

    errors = validate_private_intel_labels(sample)

    assert len(errors) == 3
    assert "note_type" in errors[0]
    assert "urgency" in errors[1]
    assert "confidence" in errors[2]
