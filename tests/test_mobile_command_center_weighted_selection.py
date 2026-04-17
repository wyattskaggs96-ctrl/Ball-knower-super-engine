import json
from pathlib import Path

from app.pipelines.mobile_command_center import build_mobile_command_center_export


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def test_mobile_command_center_prefers_weighted_scores(tmp_path: Path):
    rows_path = tmp_path / "daily_content_sheet.json"
    output_path = tmp_path / "mobile_command_center.json"

    _write_rows(
        rows_path,
        [
            {
                "topic": "Raw higher",
                "selected_hook": "hook 1",
                "postability_score": 80,
                "view_score": 99,
                "weighted_view_score": 70,
                "follow_score": 80,
                "weighted_follow_score": 65,
                "share_score": 75,
                "weighted_share_score": 60,
                "content_pack": {"caption": "cap #one"},
            },
            {
                "topic": "Weighted higher",
                "selected_hook": "hook 2",
                "postability_score": 82,
                "view_score": 10,
                "weighted_view_score": 90,
                "follow_score": 20,
                "weighted_follow_score": 88,
                "share_score": 25,
                "weighted_share_score": 89,
                "content_pack": {"caption": "cap #two"},
            },
        ],
    )

    build_mobile_command_center_export(output_path=str(output_path), source_rows_path=str(rows_path))
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["recommendations"]["views"]["topic"] == "Weighted higher"
    assert payload["recommendations"]["followers"]["topic"] == "Weighted higher"
    assert payload["recommendations"]["shares"]["topic"] == "Weighted higher"
    assert "weighted_view_score" in payload["recommendations"]["views"]["why_selected"]


def test_mobile_command_center_falls_back_to_raw_when_weighted_missing(tmp_path: Path):
    rows_path = tmp_path / "daily_content_sheet.json"
    output_path = tmp_path / "mobile_command_center.json"

    _write_rows(
        rows_path,
        [
            {
                "topic": "Raw winner",
                "selected_hook": "hook 1",
                "postability_score": 81,
                "view_score": 95,
                "follow_score": 90,
                "share_score": 92,
                "content_pack": {"caption": "cap #one"},
            },
            {
                "topic": "Raw loser",
                "selected_hook": "hook 2",
                "postability_score": 82,
                "view_score": 10,
                "follow_score": 15,
                "share_score": 20,
                "content_pack": {"caption": "cap #two"},
            },
        ],
    )

    build_mobile_command_center_export(output_path=str(output_path), source_rows_path=str(rows_path))
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["recommendations"]["views"]["topic"] == "Raw winner"
    assert payload["recommendations"]["followers"]["topic"] == "Raw winner"
    assert payload["recommendations"]["shares"]["topic"] == "Raw winner"
    assert "view_score" in payload["recommendations"]["views"]["why_selected"]
