from __future__ import annotations

from dataclasses import asdict

from email_agent.agent import EmailOrchestrationAgent, InteractionPort
from email_agent.models import EmailRequest
from email_agent.storage import ContactDirectory


class ConsoleIO(InteractionPort):
    def ask(self, prompt: str) -> str:
        return input(f"{prompt} ").strip()

    def confirm(self, prompt: str) -> bool:
        while True:
            value = input(f"{prompt} [y/n] ").strip().lower()
            if value in {"y", "yes"}:
                return True
            if value in {"n", "no"}:
                return False

    def choose(self, prompt: str, choices: list[str]) -> int:
        print(prompt)
        for index, choice in enumerate(choices, start=1):
            print(f"  {index}. {choice}")
        while True:
            raw = input("Choose an option number: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(choices):
                return int(raw) - 1


def main() -> None:
    io = ConsoleIO()
    agent = EmailOrchestrationAgent(ContactDirectory("contacts.json"))

    subject = io.ask("Email subject:")
    body = io.ask("Email body:")
    recipient_name = io.ask("Recipient name:")

    prepared = agent.prepare_email(
        io,
        EmailRequest(subject=subject, body=body, recipient_name=recipient_name),
    )

    print("\nPrepared email:")
    print(asdict(prepared))


if __name__ == "__main__":
    main()
