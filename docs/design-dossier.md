# Design Dossier

## Goals

- Build a reusable email automation agent that can run in CLI, chat, API, or UI workflows.
- Ensure the agent **always** gathers required scheduling and recipient context.
- Persist discovered contact information for future reuse.
- Detect action-oriented messages and support action completion acknowledgement loops.
- Keep implementation adapter-driven to scale across teams/environments.

## Core Design Principles

1. **Ports and adapters**
   - `InteractionPort` isolates conversational IO from business logic.
   - `ContactDirectory`, scheduler, sender, and notifier are independent abstractions.
2. **Deterministic orchestration flow**
   - Recipient -> CC/BCC -> tone -> date/time -> follow-up -> body augmentation.
3. **Progressive detail gathering**
   - Only asks for missing values.
   - Confirms existing values where required (tone/date/time confirmation).
4. **Operational safety**
   - Strict email/date/time validation.
   - Retry loops for malformed input.
5. **Scalability by replacement**
   - JSON store can be replaced by DB/CRM.
   - In-memory scheduler can be replaced with distributed schedulers.

## Component Diagram (Logical)

- **EmailOrchestrationAgent**
  - Resolves people and required metadata.
  - Triggers follow-up recommendation logic.
  - Produces `PreparedEmail`.
- **ContactDirectory**
  - `search_by_name()` and `upsert()`.
- **Follow-up intelligence**
  - `seems_action_oriented()` keyword heuristic.
  - `suggested_follow_up()` defaults.
- **Execution layer**
  - `EmailScheduler` schedules `PreparedEmail`.
  - `EmailSender` sends payload.
- **Confirmation loop**
  - `ActionConfirmationTracker` links outbound message IDs to initiating users.
  - `ActionConfirmationNotifier` informs users when recipient confirms completion.

## Data Lifecycle

1. User provides intent and partial context.
2. Agent resolves recipient/CC/BCC and stores new addresses.
3. Agent confirms tone/date/time.
4. Agent evaluates whether email is action-oriented.
5. Agent suggests follow-up plan if action-oriented.
6. Agent appends action confirmation sentence if needed.
7. Scheduler queues email.
8. Sender dispatches email.
9. Tracker stores message ID ↔ user ID mapping.
10. On inbound confirmation, notifier alerts the user.

## Trade-offs

- Keyword-based action detection is intentionally simple and explainable.
  - Pros: fast, deterministic, transparent.
  - Cons: may miss nuanced semantics.
- JSON contact store is local and lightweight.
  - Pros: zero external dependency.
  - Cons: not ideal for multi-instance consistency; replace with DB in production.

## Extension Strategy

- Add LLM/NLP classifier for action detection confidence scoring.
- Integrate OAuth + provider APIs (SES/SendGrid/Gmail).
- Add tenant isolation and RBAC for enterprise usage.
- Replace polling/CLI confirmation with webhook ingestion endpoints.
