from __future__ import annotations

import re
from datetime import datetime

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class ValidationError(ValueError):
    pass


def validate_email(email: str) -> str:
    normalized = email.strip()
    if not EMAIL_PATTERN.match(normalized):
        raise ValidationError(f"Invalid email address: {email}")
    return normalized


def parse_date(date_value: str):
    try:
        return datetime.strptime(date_value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError("Date must be in YYYY-MM-DD format.") from exc


def parse_time(time_value: str):
    try:
        return datetime.strptime(time_value.strip(), "%H:%M").time()
    except ValueError as exc:
        raise ValidationError("Time must be in HH:MM (24h) format.") from exc
