from __future__ import annotations

from datetime import time

from email_agent.models import FollowUpPlan

ACTION_KEYWORDS = {
    "approve",
    "review",
    "confirm",
    "complete",
    "deliver",
    "send",
    "submit",
    "finish",
    "respond",
}


def seems_action_oriented(text: str) -> bool:
    tokens = {word.strip(".,!?;:").lower() for word in text.split()}
    return len(tokens.intersection(ACTION_KEYWORDS)) > 0


def suggested_follow_up() -> FollowUpPlan:
    return FollowUpPlan(enabled=True, frequency="every 2 days", time_of_day=time(hour=10, minute=0))
