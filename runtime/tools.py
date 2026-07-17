from __future__ import annotations

from collections.abc import Callable

from .models import ToolResult
from .permissions import PermissionBroker
from .store import ContextStore


class ToolRegistry:
    def __init__(self, store: ContextStore, permissions: PermissionBroker) -> None:
        self.store = store
        self.permissions = permissions
        self._tools: dict[str, tuple[str, Callable[..., ToolResult]]] = {
            "search_context": ("context.read", self.search_context),
            "summarize_screen": ("screen.read", self.summarize_screen),
            "create_reminder": ("reminders.write", self.create_reminder),
            "open_document": ("documents.open", self.open_document),
        }

    def execute(self, name: str, request_id: str, **kwargs) -> ToolResult:
        permission, fn = self._tools[name]
        allowed = self.permissions.check(permission)
        self.store.audit(request_id, permission, name, "allowed" if allowed else "denied")
        if not allowed:
            return ToolResult(name=name, ok=False, content=f"Permission denied: {permission}")
        return fn(**kwargs)

    def search_context(self, query: str, limit: int = 5) -> ToolResult:
        matches = self.store.search(query, limit=limit)
        if not matches:
            return ToolResult("search_context", True, "No matching local context found.", {"matches": []})
        bullets = [
            f"- {m['title']} ({m['app']}): {m['body']}"
            for m in matches
        ]
        return ToolResult("search_context", True, "\n".join(bullets), {"matches": matches})

    def summarize_screen(self) -> ToolResult:
        matches = self.store.search("screen current profiling performance", limit=1)
        if not matches:
            return ToolResult("summarize_screen", True, "No screen snapshot is available.", {"matches": []})
        item = matches[0]
        return ToolResult(
            "summarize_screen",
            True,
            f"Your current screen appears to be {item['title']}. Key detail: {item['body']}",
            {"matches": matches},
        )

    def create_reminder(self, text: str, due_hint: str = "later") -> ToolResult:
        reminder = self.store.create_reminder(text, due_hint)
        return ToolResult(
            "create_reminder",
            True,
            f"Created reminder #{reminder['id']}: {reminder['text']} ({reminder['due_hint']}).",
            {"reminder": reminder},
        )

    def open_document(self, query: str) -> ToolResult:
        matches = [m for m in self.store.search(query, limit=5) if m["kind"] == "document"]
        if not matches:
            return ToolResult("open_document", True, "I could not find a matching local document.", {"matches": []})
        doc = matches[0]
        return ToolResult(
            "open_document",
            True,
            f"Opened {doc['title']} from {doc['source']}. Summary: {doc['body']}",
            {"document": doc},
        )
