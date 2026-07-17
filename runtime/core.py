from __future__ import annotations

from pathlib import Path

from .models import RequestTrace
from .permissions import PermissionBroker
from .planner import IntentPlanner
from .seed import SEED_CONTEXT
from .store import ContextStore
from .tools import ToolRegistry


class AssistantRuntime:
    def __init__(self, db_path: str | Path = ":memory:", seed: bool = True) -> None:
        self.store = ContextStore(db_path)
        self.permissions = PermissionBroker()
        self.planner = IntentPlanner()
        self.tools = ToolRegistry(self.store, self.permissions)
        if seed and self.store.count_context() == 0:
            for item in SEED_CONTEXT:
                self.store.add_context(item)

    def handle(self, query: str) -> dict:
        trace = RequestTrace()
        plan = self.planner.plan(query)
        trace.mark("intent_planning")
        result = self.tools.execute(plan["tool"], trace.request_id, **plan["args"])
        trace.mark("tool_execution")
        answer = self._compose_answer(query, plan["intent"], result.content)
        trace.mark("response_composition")
        return {
            "request_id": trace.request_id,
            "intent": plan["intent"],
            "tool": result.name,
            "ok": result.ok,
            "answer": answer,
            "tool_output": result.content,
            "data": result.data,
            "timings_ms": trace.timings_ms(),
            "audit": self.store.recent_audit(),
        }

    def _compose_answer(self, query: str, intent: str, content: str) -> str:
        if intent == "context_question":
            return f"Based on your local context, I found:\n{content}"
        if intent == "screen_awareness":
            return content
        if intent == "create_reminder":
            return content
        if intent == "open_document":
            return content
        return f"{content}\n\nRequest: {query}"
