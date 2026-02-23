# EmailAgent

A reusable Python agent that collects missing details, resolves stored contacts, and schedules an email for a specific date and time.

## What it supports

- Recipient resolution by name with stored-contact confirmation.
- Multi-match disambiguation and no-match fallback to ask for email.
- Automatic persistence of new/updated contacts in a local directory (`contacts.json`).
- Optional CC and BCC collection using the same resolution flow.
- Tone selection when not explicitly provided (with confirmation of provided tone).
- Date and time confirmation (with validation + re-prompt).
- Action-oriented email detection to propose follow-up reminders.
- Automatic insertion of an action confirmation sentence when the email requests action.
- Confirmation tracking hook for informing the initiating user once a recipient confirms completion.

## Architecture (scalable)

- `EmailOrchestrationAgent`: business logic for requirement gathering and validation.
- `InteractionPort`: pluggable IO contract so the same logic can run in CLI, API, chat, or voice apps.
- `ContactDirectory`: persistence abstraction (JSON now, replaceable with DB/CRM adapters).
- `EmailScheduler`: scheduling abstraction (replace with Celery/Cloud Tasks).
- `EmailSender`, `ActionConfirmationTracker`, and `ActionConfirmationNotifier`: integration hooks for delivery and user notifications.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
pip install -e .
PYTHONPATH=src python -m email_agent.cli
```

## Dossiers

- Design Dossier: `docs/design-dossier.md`
- Specification Dossier: `docs/specification-dossier.md`
- Testing Dossier: `docs/testing-dossier.md`
- Installation & Deployment Dossier: `docs/installation-dossier.md`

## GitHub Codespaces startup

This repository includes a Codespaces startup setup:

- `.devcontainer/devcontainer.json` runs `scripts/codespaces-startup.sh` after creation.
- The startup script creates `.venv`, installs the package, and writes `.codespaces/agent-env`.

After Codespace starts, run:

```bash
source .venv/bin/activate
source .codespaces/agent-env
```

