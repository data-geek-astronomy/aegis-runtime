from __future__ import annotations

import re


class IntentPlanner:
    def plan(self, query: str) -> dict:
        text = query.strip()
        lowered = text.lower()

        if any(phrase in lowered for phrase in ["screen", "on my display", "current window"]):
            return {"tool": "summarize_screen", "args": {}, "intent": "screen_awareness"}

        if "remind" in lowered or "reminder" in lowered:
            due_hint = self._extract_due_hint(lowered)
            reminder_text = re.sub(r"^remind me to\s+", "", text, flags=re.I).strip()
            return {
                "tool": "create_reminder",
                "args": {"text": reminder_text or text, "due_hint": due_hint},
                "intent": "create_reminder",
            }

        if any(word in lowered for word in ["open", "document", "doc", "file"]):
            return {"tool": "open_document", "args": {"query": text}, "intent": "open_document"}

        return {"tool": "search_context", "args": {"query": self._focused_query(text), "limit": 5}, "intent": "context_question"}

    def _extract_due_hint(self, lowered: str) -> str:
        for marker in ["after ", "tomorrow", "today", "friday", "next week", "later"]:
            if marker in lowered:
                return marker if marker != "after " else "after " + lowered.split("after ", 1)[1]
        return "later"

    def _focused_query(self, text: str) -> str:
        cleaned = re.sub(r"\b(what|did|i|discuss|about|with|summarize|find|show|me|the)\b", " ", text, flags=re.I)
        return " ".join(cleaned.split()) or text
