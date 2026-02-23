# Specification Dossier

## Functional Requirements

### FR-1 Recipient resolution
- Input: recipient name (+ optional recipient email).
- Behavior:
  - If one email exists for the name: ask for confirmation.
  - If multiple emails exist: ask user to select one.
  - If none exists: ask for email.
  - Any newly provided email is persisted.

### FR-2 CC/BCC collection
- If not explicitly given, ask user whether to add CC and BCC recipients.
- For each CC/BCC name, run the exact same contact resolution logic as recipient.
- Persist any newly supplied emails.

### FR-3 Tone selection
- If tone is absent, present fixed options:
  - formal, friendly, persuasive, concise.
- If tone is provided, request user confirmation.

### FR-4 Date confirmation
- If date is provided, ask user to confirm.
- If not confirmed or not provided, ask for date in `YYYY-MM-DD`.
- Validate and re-prompt on invalid format.

### FR-5 Time confirmation
- If time is provided, ask user to confirm.
- If not confirmed or not provided, ask for time in `HH:MM` (24-hour).
- Validate and re-prompt on invalid format.

### FR-6 Follow-up suggestion
- Determine if message is action-oriented.
- If action-oriented and follow-up is not explicitly supplied:
  - Ask if user wants a follow-up.
  - Provide default recommendation (every 2 days at 10:00).
  - Capture custom frequency/time.

### FR-7 Action confirmation request in body
- If message is action-oriented, append a sentence requesting completion confirmation and status update.

### FR-8 Notify original user when action confirmation arrives
- Track outbound message IDs to user IDs.
- On inbound confirmation event, notify the original user and close tracking record.

## Non-Functional Requirements

- **NFR-1 Reusability:** business logic independent from transport channel.
- **NFR-2 Data correctness:** strict validation for email/date/time.
- **NFR-3 Deployability:** support local CLI now; adapter-friendly for service deployment.
- **NFR-4 Observability-ready:** components are separable for structured logging and metrics additions.

## Validation Rules

- Email must satisfy canonical pattern `<local>@<domain>.<tld>`.
- Date must parse via `%Y-%m-%d`.
- Time must parse via `%H:%M`.
- Invalid values require re-prompting.

## State Model (simplified)

`Draft Request` -> `Recipient Resolved` -> `CC/BCC Resolved` -> `Tone Confirmed` -> `Schedule Confirmed` -> `Follow-up Decided` -> `Prepared` -> `Scheduled` -> `Sent` -> (`Awaiting Action Confirmation` | `Completed`)

## Interfaces

- `InteractionPort.ask(prompt) -> str`
- `InteractionPort.confirm(prompt) -> bool`
- `InteractionPort.choose(prompt, choices) -> int`
- `ContactDirectory.search_by_name(name) -> list[Contact]`
- `ContactDirectory.upsert(contact)`
- `ActionConfirmationTracker.register(message_id, user_id)`
- `ActionConfirmationTracker.process_confirmation(message_id, confirmation_text, notifier) -> bool`
