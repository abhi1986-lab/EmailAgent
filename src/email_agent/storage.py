from __future__ import annotations

import json
from pathlib import Path

from email_agent.models import Contact
from email_agent.validators import validate_email


class ContactDirectory:
    """Simple JSON-backed contact store.

    The file format is intentionally minimal so it can be used in CLI, API, or serverless contexts.
    """

    def __init__(self, path: str | Path = "contacts.json") -> None:
        self.path = Path(path)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict[str, str]]:
        return json.loads(self.path.read_text() or "[]")

    def _write(self, contacts: list[dict[str, str]]) -> None:
        self.path.write_text(json.dumps(contacts, indent=2))

    def search_by_name(self, name: str) -> list[Contact]:
        target = name.strip().lower()
        matches: list[Contact] = []
        for row in self._read():
            if row["name"].strip().lower() == target:
                matches.append(Contact(name=row["name"], email=row["email"]))
        return matches

    def upsert(self, contact: Contact) -> None:
        rows = self._read()
        normalized_email = validate_email(contact.email).lower()
        for row in rows:
            if row["email"].strip().lower() == normalized_email:
                row["name"] = contact.name
                row["email"] = normalized_email
                self._write(rows)
                return
        rows.append({"name": contact.name, "email": normalized_email})
        self._write(rows)
