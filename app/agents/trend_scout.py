from __future__ import annotations

from app.core.models import TrendCandidate
from app.core.utils import make_fingerprint, normalize_topic
from app.db.repository import Repository
from app.sources import manual_source, reddit_source, rss_source


class TrendScoutAgent:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def gather(self, enable_rss: bool, enable_reddit: bool, enable_manual: bool) -> list[TrendCandidate]:
        candidates: list[TrendCandidate] = []
        if enable_rss:
            candidates.extend(rss_source.fetch_trends())
        if enable_reddit:
            candidates.extend(reddit_source.fetch_trends())
        if enable_manual:
            candidates.extend(manual_source.fetch_trends())
        return candidates

    def normalize(self, trends: list[TrendCandidate]) -> list[TrendCandidate]:
        normalized: list[TrendCandidate] = []
        for trend in trends:
            topic = normalize_topic(trend.topic)
            trend.topic = topic.capitalize()
            trend.fingerprint = make_fingerprint("global", topic)
            normalized.append(trend)
        return normalized

    def dedupe(self, trends: list[TrendCandidate]) -> list[TrendCandidate]:
        seen: set[str] = set()
        deduped: list[TrendCandidate] = []
        for trend in trends:
            if trend.fingerprint in seen:
                continue
            seen.add(trend.fingerprint or "")
            deduped.append(trend)
        return deduped

    def run(self, enable_rss: bool, enable_reddit: bool, enable_manual: bool) -> list[int]:
        trends = self.gather(enable_rss, enable_reddit, enable_manual)
        trends = self.normalize(trends)
        trends = self.dedupe(trends)
        return self.repo.insert_trend_candidates(trends)
