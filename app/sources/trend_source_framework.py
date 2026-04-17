from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from app.core.models import TrendCandidate
from app.core.utils import normalize_topic


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrendSourceDefinition:
    source_name: str
    source_type: str
    source_priority: int
    fetcher: Callable[[], list[TrendCandidate]]
    enabled_env_var: str | None = None


MAX_SUPPORTED_SOURCES = 10


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_enabled(source: TrendSourceDefinition) -> bool:
    if not source.enabled_env_var:
        return True
    return _as_bool(os.getenv(source.enabled_env_var), False)


def _apply_metadata(trend: TrendCandidate, source: TrendSourceDefinition) -> TrendCandidate:
    source_timestamp = trend.source_timestamp or trend.discovered_at or datetime.now(timezone.utc)
    return trend.model_copy(
        update={
            "source": trend.source or source.source_name,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "source_priority": source.source_priority,
            "source_timestamp": source_timestamp,
        }
    )


def collect_trends(sources: list[TrendSourceDefinition]) -> tuple[list[TrendCandidate], dict[str, dict[str, int | bool]]]:
    if len(sources) > MAX_SUPPORTED_SOURCES:
        raise ValueError(f"Configured {len(sources)} sources, but max supported is {MAX_SUPPORTED_SOURCES}.")

    ranked_sources = sorted(sources, key=lambda source: source.source_priority)
    deduped: list[TrendCandidate] = []
    seen_topics: set[str] = set()
    contribution_report: dict[str, dict[str, int | bool]] = {}

    for source in ranked_sources:
        enabled = _is_enabled(source)
        source_report: dict[str, int | bool] = {"enabled": enabled, "fetched": 0, "ingested": 0}

        if not enabled:
            contribution_report[source.source_name] = source_report
            continue

        try:
            fetched = source.fetcher()
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.warning("Trend source '%s' failed: %s", source.source_name, exc)
            contribution_report[source.source_name] = source_report
            continue

        source_report["fetched"] = len(fetched)
        for trend in fetched:
            enriched = _apply_metadata(trend, source)
            normalized = normalize_topic(enriched.topic)
            if normalized in seen_topics:
                continue
            seen_topics.add(normalized)
            deduped.append(enriched)
            source_report["ingested"] = int(source_report["ingested"]) + 1

        contribution_report[source.source_name] = source_report

    return deduped, contribution_report
