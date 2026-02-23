from email_agent.services import ActionConfirmationNotifier, ActionConfirmationTracker


class RecordingNotifier(ActionConfirmationNotifier):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def notify_user(self, user_id: str, status_message: str) -> None:
        self.calls.append((user_id, status_message))


def test_process_confirmation_notifies_registered_user():
    tracker = ActionConfirmationTracker()
    notifier = RecordingNotifier()

    tracker.register(message_id="msg-1", user_id="user-9")

    processed = tracker.process_confirmation(
        message_id="msg-1",
        confirmation_text="Task completed",
        notifier=notifier,
    )

    assert processed is True
    assert notifier.calls == [("user-9", "Task completed")]


def test_process_confirmation_ignores_unknown_messages():
    tracker = ActionConfirmationTracker()
    notifier = RecordingNotifier()

    processed = tracker.process_confirmation(
        message_id="unknown",
        confirmation_text="Done",
        notifier=notifier,
    )

    assert processed is False
    assert notifier.calls == []
