from __future__ import annotations

import json
import sqlite3
from typing import Iterable, List

from app.core.models import ContentPack, Hook, TrendCandidate, TrendScore


class Repository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert_trend_candidates(self, trends: Iterable[TrendCandidate]) -> list[int]:
        ids: list[int] = []
        for trend in trends:
            cur = self.conn.execute(
                """
                INSERT OR IGNORE INTO trend_candidates
                (source, topic, summary, url, sport, discovered_at, fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trend.source,
                    trend.topic,
                    trend.summary,
                    trend.url,
                    trend.sport,
                    trend.discovered_at.isoformat(),
                    trend.fingerprint,
                ),
            )
            if cur.lastrowid:
                ids.append(cur.lastrowid)
        self.conn.commit()
        return ids

    def list_trend_candidates(self) -> List[TrendCandidate]:
        rows = self.conn.execute("SELECT * FROM trend_candidates ORDER BY id DESC").fetchall()
        return [TrendCandidate(**dict(r)) for r in rows]

    def get_trend_candidate(self, trend_id: int) -> TrendCandidate | None:
        row = self.conn.execute("SELECT * FROM trend_candidates WHERE id = ?", (trend_id,)).fetchone()
        return TrendCandidate(**dict(row)) if row else None

    def insert_trend_score(self, score: TrendScore) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO trend_scores
            (trend_candidate_id, recency, audience_fit, virality, controversy,
             recognition, ease_of_execution, total_score, reasoning, recommended, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                score.trend_candidate_id,
                score.recency,
                score.audience_fit,
                score.virality,
                score.controversy,
                score.recognition,
                score.ease_of_execution,
                score.total_score,
                score.reasoning,
                int(score.recommended),
                score.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_recommended_scores(self, threshold: float) -> List[TrendScore]:
        rows = self.conn.execute(
            "SELECT * FROM trend_scores WHERE total_score >= ? ORDER BY total_score DESC", (threshold,)
        ).fetchall()
        return [TrendScore(**dict(r)) for r in rows]

    def latest_score_for_trend(self, trend_id: int) -> TrendScore | None:
        row = self.conn.execute(
            "SELECT * FROM trend_scores WHERE trend_candidate_id = ? ORDER BY id DESC LIMIT 1", (trend_id,)
        ).fetchone()
        return TrendScore(**dict(row)) if row else None

    def insert_hook(self, hook: Hook) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO hooks (trend_candidate_id, trend_score_id, hook_text, style, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                hook.trend_candidate_id,
                hook.trend_score_id,
                hook.hook_text,
                hook.style,
                hook.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_hooks_for_trend(self, trend_id: int) -> List[Hook]:
        rows = self.conn.execute(
            "SELECT * FROM hooks WHERE trend_candidate_id = ? ORDER BY id DESC", (trend_id,)
        ).fetchall()
        return [Hook(**dict(r)) for r in rows]

    def get_hook(self, hook_id: int) -> Hook | None:
        row = self.conn.execute("SELECT * FROM hooks WHERE id = ?", (hook_id,)).fetchone()
        return Hook(**dict(row)) if row else None

    def insert_content_pack(self, pack: ContentPack) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO content_packs
            (trend_candidate_id, hook_id, overlay_lines, caption, cta, creator_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pack.trend_candidate_id,
                pack.hook_id,
                json.dumps(pack.overlay_lines),
                pack.caption,
                pack.cta,
                pack.creator_notes,
                pack.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_content_packs(self, ids: list[int] | None = None) -> List[ContentPack]:
        if ids:
            placeholders = ",".join("?" for _ in ids)
            rows = self.conn.execute(
                f"SELECT * FROM content_packs WHERE id IN ({placeholders}) ORDER BY id DESC", ids
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM content_packs ORDER BY id DESC").fetchall()

        packs: list[ContentPack] = []
        for row in rows:
            payload = dict(row)
            payload["overlay_lines"] = json.loads(payload["overlay_lines"])
            packs.append(ContentPack(**payload))
        return packs
