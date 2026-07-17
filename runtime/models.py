from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ContextItem:
    source: str
    title: str
    body: str
    kind: str = "note"
    people: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    created_at: str = ""
    app: str = "local"


@dataclass(frozen=True)
class ToolResult:
    name: str
    ok: bool
    content: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestTrace:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    marks: list[tuple[str, float]] = field(default_factory=list)
    started: float = field(default_factory=perf_counter)

    def mark(self, label: str) -> None:
        self.marks.append((label, perf_counter()))

    def timings_ms(self) -> dict[str, float]:
        previous = self.started
        timings: dict[str, float] = {}
        for label, timestamp in self.marks:
            timings[label] = round((timestamp - previous) * 1000, 2)
            previous = timestamp
        timings["total"] = round((previous - self.started) * 1000, 2)
        return timings
