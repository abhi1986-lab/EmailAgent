from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class Tone(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "friendly"
    PERSUASIVE = "persuasive"
    CONCISE = "concise"


@dataclass
class Contact:
    name: str
    email: str


@dataclass
class FollowUpPlan:
    enabled: bool
    frequency: str | None = None
    time_of_day: time | None = None


@dataclass
class EmailRequest:
    subject: str
    body: str
    recipient_name: str | None = None
    recipient_email: str | None = None
    cc_names: list[str] = field(default_factory=list)
    bcc_names: list[str] = field(default_factory=list)
    cc_emails: list[str] = field(default_factory=list)
    bcc_emails: list[str] = field(default_factory=list)
    tone: Tone | None = None
    send_date: date | None = None
    send_time: time | None = None
    follow_up: FollowUpPlan | None = None


@dataclass
class PreparedEmail:
    to: Contact
    cc: list[Contact]
    bcc: list[Contact]
    subject: str
    body: str
    scheduled_date: date
    scheduled_time: time
    tone: Tone
    follow_up: FollowUpPlan
    ask_for_action_confirmation: bool
