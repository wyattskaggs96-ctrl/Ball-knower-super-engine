import json
from pathlib import Path

from app.pipelines.simulate_daily_sheet import simulate_daily_content_sheet


def test_simulation_writes_expected_files(tmp_path: Path):
    out = tmp_path / "example_output.md"
    result = simulate_daily_content_sheet(str(out))
    assert result["top_topics"] == 10
    assert out.exists()
    assert out.with_suffix(".json").exists()
    assert (out.parent / "video_blueprint.json").exists()
    assert (out.parent / "daily_post_ready.md").exists()
    assert (out.parent / "top_5_post_now.md").exists()
    assert (out.parent / "top_3_views.md").exists()
    assert (out.parent / "top_3_follows.md").exists()
    assert (out.parent / "top_3_shares.md").exists()

    rows = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert all("postability_score" in row for row in rows)
    assert all("view_score" in row for row in rows)
    assert all("follow_score" in row for row in rows)
    assert all("share_score" in row for row in rows)
    assert all("primary_goal" in row for row in rows)
    assert all(len(row["hooks"]) == 5 for row in rows)
