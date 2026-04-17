from pathlib import Path

from app.pipelines.private_intel_ingestion import build_private_intel_report_payload, export_private_intel_report
from app.sources.private_intel_source import load_private_intel, normalize_private_intel_items


def test_private_intel_load_and_normalize():
    items = load_private_intel()
    normalized = normalize_private_intel_items(items)

    assert len(items) >= 3
    assert len(items) == len(normalized)
    assert all(item.source_type == "private_intel" for item in normalized)


def test_private_intel_payload_sections():
    payload = build_private_intel_report_payload()

    assert "all_private_intel_items" in payload
    assert "highest_urgency_items" in payload
    assert "highest_confidence_items" in payload
    assert "likely_recruiting_or_portal_moves" in payload
    assert "likely_stories_to_post_before_mainstream" in payload


def test_private_intel_export_files(tmp_path: Path):
    md_path, json_path = export_private_intel_report(export_dir=tmp_path)

    assert md_path.exists()
    assert json_path.exists()
    assert "Private Intel Report" in md_path.read_text(encoding="utf-8")
