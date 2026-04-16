from __future__ import annotations

from datetime import timedelta


SCHEDULE_EVERY_HOURS = 2


def schedule_stub() -> dict[str, str]:
    return {
        "interval": str(timedelta(hours=SCHEDULE_EVERY_HOURS)),
        "note": "Stub only: wire to cron/celery/worker infra when ready.",
    }
