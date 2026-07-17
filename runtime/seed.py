from __future__ import annotations

from .models import ContextItem


SEED_CONTEXT = [
    ContextItem(
        source="mail/inbox/launch-plan",
        title="Launch planning thread with Priya",
        body="Priya asked for a tighter launch checklist, owner mapping, and a Friday review before the beta announcement.",
        kind="email",
        people=("Priya",),
        tags=("launch", "beta", "checklist"),
        created_at="2026-07-16T10:05:00",
        app="Mail",
    ),
    ContextItem(
        source="calendar/design-review",
        title="Design review with Alex",
        body="Alex suggested deferring the settings redesign and replying after the platform sync meeting.",
        kind="meeting",
        people=("Alex",),
        tags=("design", "reply", "meeting"),
        created_at="2026-07-16T13:30:00",
        app="Calendar",
    ),
    ContextItem(
        source="notes/runtime-architecture",
        title="Aegis Runtime architecture notes",
        body="Runtime goals: local-first context, permissioned tools, streaming responses, auditability, and latency budgets under 250ms for retrieval.",
        kind="note",
        people=("Aravind",),
        tags=("runtime", "latency", "privacy"),
        created_at="2026-07-15T21:15:00",
        app="Notes",
    ),
    ContextItem(
        source="files/Aegis_Runtime_Spec.md",
        title="Aegis Runtime Spec",
        body="Spec covering on-device assistant orchestration, SQLite FTS context index, screen awareness adapter, and tool execution contracts.",
        kind="document",
        people=("Aravind",),
        tags=("spec", "assistant", "document"),
        created_at="2026-07-16T18:45:00",
        app="Finder",
    ),
    ContextItem(
        source="screen/current",
        title="Current screen: Xcode performance trace",
        body="The active screen shows a timeline with retrieval taking 42ms, tool routing 7ms, and response composition 19ms.",
        kind="screen",
        people=(),
        tags=("screen", "profiling", "performance"),
        created_at="2026-07-17T09:00:00",
        app="Xcode",
    ),
]
