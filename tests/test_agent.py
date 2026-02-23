from datetime import date, time

from email_agent.agent import EmailOrchestrationAgent
from email_agent.models import Contact, EmailRequest, Tone
from email_agent.storage import ContactDirectory


class FakeIO:
    def __init__(self, asks: list[str], confirms: list[bool], choices: list[int]) -> None:
        self.asks = asks
        self.confirms = confirms
        self.choices = choices

    def ask(self, prompt: str) -> str:
        return self.asks.pop(0)

    def confirm(self, prompt: str) -> bool:
        return self.confirms.pop(0)

    def choose(self, prompt: str, choices: list[str]) -> int:
        return self.choices.pop(0)


def test_resolve_recipient_from_directory(tmp_path):
    directory = ContactDirectory(tmp_path / "contacts.json")
    directory.upsert(Contact(name="Alex", email="alex@company.com"))
    agent = EmailOrchestrationAgent(directory)
    io = FakeIO(asks=[], confirms=[True, False, False, True, True, True, False], choices=[])

    prepared = agent.prepare_email(
        io,
        EmailRequest(
            subject="FYI",
            body="Please review the draft.",
            recipient_name="Alex",
            tone=Tone.CONCISE,
            send_date=date(2026, 1, 1),
            send_time=time(9, 30),
        ),
    )

    assert prepared.to.email == "alex@company.com"
    assert prepared.ask_for_action_confirmation is True


def test_new_contact_saved_when_not_found_and_invalid_email_reprompt(tmp_path):
    directory = ContactDirectory(tmp_path / "contacts.json")
    agent = EmailOrchestrationAgent(directory)
    io = FakeIO(
        asks=["bad-email", "sam@example.com", "every day", "09:00"],
        confirms=[False, False, True, True, True, True],
        choices=[],
    )

    prepared = agent.prepare_email(
        io,
        EmailRequest(
            subject="Need update",
            body="Please complete the migration.",
            recipient_name="Sam",
            tone=Tone.FORMAL,
            send_date=date(2026, 2, 1),
            send_time=time(12, 0),
        ),
    )

    assert prepared.to.email == "sam@example.com"
    assert directory.search_by_name("Sam")[0].email == "sam@example.com"
    assert prepared.follow_up.enabled is True


def test_date_time_reprompt_when_not_confirmed(tmp_path):
    directory = ContactDirectory(tmp_path / "contacts.json")
    directory.upsert(Contact(name="Lee", email="lee@company.com"))
    agent = EmailOrchestrationAgent(directory)

    io = FakeIO(
        asks=["2026-04-10", "15:45"],
        confirms=[True, False, False, False, False, False],
        choices=[0],
    )

    prepared = agent.prepare_email(
        io,
        EmailRequest(
            subject="Reminder",
            body="General update",
            recipient_name="Lee",
            tone=Tone.FRIENDLY,
            send_date=date(2026, 3, 1),
            send_time=time(8, 0),
        ),
    )

    assert prepared.scheduled_date == date(2026, 4, 10)
    assert prepared.scheduled_time == time(15, 45)
