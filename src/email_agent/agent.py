from __future__ import annotations

from datetime import date, time
from typing import Protocol

from email_agent.followup import seems_action_oriented, suggested_follow_up
from email_agent.models import Contact, EmailRequest, FollowUpPlan, PreparedEmail, Tone
from email_agent.storage import ContactDirectory
from email_agent.validators import ValidationError, parse_date, parse_time, validate_email


class InteractionPort(Protocol):
    def ask(self, prompt: str) -> str: ...

    def confirm(self, prompt: str) -> bool: ...

    def choose(self, prompt: str, choices: list[str]) -> int: ...


class EmailOrchestrationAgent:
    def __init__(self, contact_directory: ContactDirectory) -> None:
        self.contact_directory = contact_directory

    def _collect_valid_email(self, io: InteractionPort, prompt: str) -> str:
        while True:
            candidate = io.ask(prompt)
            try:
                return validate_email(candidate)
            except ValidationError:
                # Keep the contract minimal: ask again until valid.
                continue

    def resolve_contact(
        self,
        io: InteractionPort,
        name: str,
        provided_email: str | None = None,
        role: str = "recipient",
    ) -> Contact:
        if provided_email:
            contact = Contact(name=name, email=validate_email(provided_email))
            self.contact_directory.upsert(contact)
            return contact

        matches = self.contact_directory.search_by_name(name)
        if len(matches) == 1:
            if io.confirm(
                f"I found one {role} email for {name}: {matches[0].email}. Use this address?"
            ):
                return matches[0]
            email = self._collect_valid_email(io, f"Please provide {name}'s email address:")
            contact = Contact(name=name, email=email)
            self.contact_directory.upsert(contact)
            return contact

        if len(matches) > 1:
            index = io.choose(
                f"I found multiple {role} emails for {name}. Which one should I use?",
                [m.email for m in matches],
            )
            return matches[index]

        email = self._collect_valid_email(
            io,
            f"No stored email found for {name}. Please provide the email address:",
        )
        contact = Contact(name=name, email=email)
        self.contact_directory.upsert(contact)
        return contact

    def _resolve_people_list(
        self,
        io: InteractionPort,
        role: str,
        names: list[str],
        emails: list[str],
    ) -> list[Contact]:
        contacts: list[Contact] = []
        for idx, name in enumerate(names):
            given_email = emails[idx] if idx < len(emails) else None
            contacts.append(
                self.resolve_contact(
                    io=io,
                    name=name,
                    provided_email=given_email,
                    role=role,
                )
            )
        return contacts

    def _resolve_tone(self, io: InteractionPort, tone: Tone | None) -> Tone:
        options = [tone_item.value for tone_item in Tone]
        if tone:
            if io.confirm(f"Tone is '{tone.value}'. Keep it?"):
                return tone
        choice = io.choose("Which tone should I use?", options)
        return Tone(options[choice])

    def _resolve_date(self, io: InteractionPort, send_date: date | None) -> date:
        if send_date and io.confirm(f"Send date is {send_date.isoformat()}. Confirm?"):
            return send_date
        while True:
            value = io.ask("What date should I send the email? (YYYY-MM-DD)")
            try:
                return parse_date(value)
            except ValidationError:
                continue

    def _resolve_time(self, io: InteractionPort, send_time: time | None) -> time:
        if send_time and io.confirm(f"Send time is {send_time.strftime('%H:%M')}. Confirm?"):
            return send_time
        while True:
            value = io.ask("What time should I send the email? (HH:MM 24h)")
            try:
                return parse_time(value)
            except ValidationError:
                continue

    def _resolve_follow_up(
        self,
        io: InteractionPort,
        request: EmailRequest,
        ask_for_action_confirmation: bool,
    ) -> FollowUpPlan:
        if request.follow_up:
            return request.follow_up
        if not ask_for_action_confirmation:
            return FollowUpPlan(enabled=False)

        suggested = suggested_follow_up()
        if not io.confirm(
            "This email looks action-oriented. Do you want a follow-up reminder? "
            f"Suggested: {suggested.frequency} at {suggested.time_of_day.strftime('%H:%M')}."
        ):
            return FollowUpPlan(enabled=False)

        frequency = (
            io.ask(f"How often should I follow up? (Press enter for '{suggested.frequency}')").strip()
            or suggested.frequency
        )

        while True:
            reminder_time_input = io.ask(
                f"Follow-up time (HH:MM, press enter for {suggested.time_of_day.strftime('%H:%M')}):"
            ).strip()
            if not reminder_time_input:
                reminder_time = suggested.time_of_day
                break
            try:
                reminder_time = parse_time(reminder_time_input)
                break
            except ValidationError:
                continue

        return FollowUpPlan(enabled=True, frequency=frequency, time_of_day=reminder_time)

    def prepare_email(self, io: InteractionPort, request: EmailRequest) -> PreparedEmail:
        recipient_name = request.recipient_name or io.ask("Who is the recipient?")
        recipient = self.resolve_contact(
            io=io,
            name=recipient_name,
            provided_email=request.recipient_email,
            role="recipient",
        )

        if not request.cc_names and io.confirm("Do you want to add anyone in CC?"):
            request.cc_names = [
                name.strip()
                for name in io.ask("Enter CC names (comma separated):").split(",")
                if name.strip()
            ]
        if not request.bcc_names and io.confirm("Do you want to add anyone in BCC?"):
            request.bcc_names = [
                name.strip()
                for name in io.ask("Enter BCC names (comma separated):").split(",")
                if name.strip()
            ]

        cc = self._resolve_people_list(
            io,
            role="cc recipient",
            names=request.cc_names,
            emails=request.cc_emails,
        )
        bcc = self._resolve_people_list(
            io,
            role="bcc recipient",
            names=request.bcc_names,
            emails=request.bcc_emails,
        )

        tone = self._resolve_tone(io, request.tone)
        send_date = self._resolve_date(io, request.send_date)
        send_time = self._resolve_time(io, request.send_time)

        ask_for_action_confirmation = seems_action_oriented(f"{request.subject} {request.body}")
        follow_up = self._resolve_follow_up(io, request, ask_for_action_confirmation)

        body = request.body
        if ask_for_action_confirmation:
            body = (
                f"{body}\n\n"
                "Please confirm once the action is completed, with a brief status update."
            )

        return PreparedEmail(
            to=recipient,
            cc=cc,
            bcc=bcc,
            subject=request.subject,
            body=body,
            scheduled_date=send_date,
            scheduled_time=send_time,
            tone=tone,
            follow_up=follow_up,
            ask_for_action_confirmation=ask_for_action_confirmation,
        )
