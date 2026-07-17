from __future__ import annotations


class PermissionBroker:
    def __init__(self, allowed: set[str] | None = None) -> None:
        self.allowed = allowed or {
            "context.read",
            "screen.read",
            "documents.open",
            "reminders.write",
        }

    def check(self, permission: str) -> bool:
        return permission in self.allowed
