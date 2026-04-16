from pathlib import Path

from app.pipelines.simulate_daily_sheet import simulate_daily_content_sheet


def test_simulation_writes_expected_files(tmp_path: Path):
    out = tmp_path / "example_output.md"
    result = simulate_daily_content_sheet(str(out))
    assert result["top_topics"] == 10
    assert out.exists()
    assert out.with_suffix(".json").exists()
    assert (out.parent / "video_blueprint.json").exists()
