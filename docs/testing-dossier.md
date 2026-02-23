# Testing Dossier

## Test Strategy

This project uses unit tests to validate critical orchestration behavior and edge handling.

### Current automated test scope

1. Recipient resolution from existing contact store.
2. New contact capture and persistence.
3. Action-oriented detection path and follow-up enablement.

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
pip install -e .
```

## Execute tests

```bash
pytest -q
```

## Recommended Additional Tests (high priority)

1. **Validation tests**
   - Invalid email is rejected until valid input is provided.
   - Invalid date/time prompt loops.
2. **Disambiguation tests**
   - Multiple email matches for same name uses `choose()` path.
3. **Tone/date/time confirmation tests**
   - Provided values are retained when confirmed.
   - Provided values are replaced when rejected.
4. **CC/BCC tests**
   - CC/BCC optional prompts work when empty.
   - Provided CC/BCC names and mixed email availability resolve correctly.
5. **Action confirmation tracking tests**
   - Register + process confirmation triggers notifier exactly once.
   - Unknown message IDs are ignored safely.

## Example targeted command set

```bash
pytest -q tests/test_agent.py
pytest -q -k follow_up
pytest -q -k contact
```

## Manual test checklist

1. Start CLI.
2. Enter recipient name with no existing contact; provide email.
3. Add CC/BCC recipients and verify prompting behavior.
4. Skip tone initially and choose from provided list.
5. Enter date/time and verify formatting constraints.
6. Use an action-oriented body (e.g., "Please complete the report") and verify:
   - Follow-up suggestion prompt appears.
   - Confirmation sentence is appended to final body.
7. Confirm the generated payload structure from CLI output.

## CI recommendation

- Run `pytest -q` on every pull request.
- Enforce formatting/linting (e.g., `ruff`, `black`) in a future iteration.
