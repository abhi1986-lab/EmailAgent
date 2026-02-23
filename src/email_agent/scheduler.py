from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from email_agent.models import PreparedEmail


@dataclass
class ScheduledTask:
    run_at: datetime
    payload: PreparedEmail


class EmailScheduler:
    """In-memory scheduler abstraction.

    Replace this class with Celery/Cloud Tasks/Quartz adapters in production.
    """

    def __init__(self) -> None:
        self.tasks: list[ScheduledTask] = []

    def schedule(self, prepared_email: PreparedEmail, callback: Callable[[PreparedEmail], None]) -> ScheduledTask:
        run_at = datetime.combine(prepared_email.scheduled_date, prepared_email.scheduled_time)
        task = ScheduledTask(run_at=run_at, payload=prepared_email)
        self.tasks.append(task)
        callback(prepared_email)
        return task
