from __future__ import annotations

from app.services.content_service import ContentService
from app.services.trend_service import TrendService


def run_daily_pipeline(trend_service: TrendService, content_service: ContentService, score_threshold: float) -> dict:
    inserted_ids = trend_service.scout_trends()
    recommendations = content_service.score(threshold=score_threshold)

    hooks_created = 0
    packs_created = 0

    for recommendation in recommendations:
        hooks = content_service.generate_hooks(recommendation.trend_candidate_id)
        hooks_created += len(hooks)
        if hooks:
            pack = content_service.generate_script(hooks[0].id)
            if pack:
                packs_created += 1

    return {
        "inserted_trends": len(inserted_ids),
        "recommended_topics": len(recommendations),
        "hooks_created": hooks_created,
        "packs_created": packs_created,
    }
