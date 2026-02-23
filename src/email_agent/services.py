from __future__ import annotations

from dataclasses import dataclass

from email_agent.models import PreparedEmail


@dataclass
class DeliveryResult:
    message_id: str


class EmailSender:
    def send(self, email: PreparedEmail) -> DeliveryResult:
        """Placeholder for SMTP/provider integration."""
        return DeliveryResult(message_id="mock-message-id")


class ActionConfirmationNotifier:
    """Hook for notifying the original user when recipient confirms an action."""

    def notify_user(self, user_id: str, status_message: str) -> None:
        # In production, forward to app notifications / Slack / webhook.
        print(f"Notify {user_id}: {status_message}")


class ActionConfirmationTracker:
    """Tracks action-oriented sent emails to map recipient confirmations back to requesters."""

    def __init__(self) -> None:
        self.pending: dict[str, str] = {}

    def register(self, message_id: str, user_id: str) -> None:
        self.pending[message_id] = user_id

    def process_confirmation(
        self,
        message_id: str,
        confirmation_text: str,
        notifier: ActionConfirmationNotifier,
    ) -> bool:
        user_id = self.pending.pop(message_id, None)
        if not user_id:
            return False
        notifier.notify_user(user_id=user_id, status_message=confirmation_text)
        return True
