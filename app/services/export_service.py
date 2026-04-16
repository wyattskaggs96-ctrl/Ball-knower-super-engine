from __future__ import annotations

import json
from pathlib import Path

from app.core.models import ContentPack
from app.db.repository import Repository


class ExportService:
    def __init__(self, repo: Repository, export_dir: str) -> None:
        self.repo = repo
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _select(self, ids: list[int] | None) -> list[ContentPack]:
        return self.repo.list_content_packs(ids=ids)

    def export_json(self, ids: list[int] | None = None, filename: str = "content_packs.json") -> str:
        packs = [p.model_dump(mode="json") for p in self._select(ids)]
        path = self.export_dir / filename
        path.write_text(json.dumps(packs, indent=2), encoding="utf-8")
        return str(path)

    def export_markdown(self, ids: list[int] | None = None, filename: str = "content_packs.md") -> str:
        packs = self._select(ids)
        lines = ["# Ball Knower Engine Content Packs", ""]
        for pack in packs:
            lines.append(f"## Pack #{pack.id}")
            lines.append(f"- Trend ID: {pack.trend_candidate_id}")
            lines.append(f"- Hook ID: {pack.hook_id}")
            lines.append("- Overlay Lines:")
            for line in pack.overlay_lines:
                lines.append(f"  - {line}")
            lines.append(f"- Caption: {pack.caption}")
            lines.append(f"- CTA: {pack.cta}")
            lines.append(f"- Creator Notes: {pack.creator_notes}")
            lines.append("")

        path = self.export_dir / filename
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)
