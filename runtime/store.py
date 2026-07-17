from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import ContextItem


class ContextStore:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            create table if not exists context_items (
                id integer primary key,
                source text not null,
                title text not null,
                body text not null,
                kind text not null,
                people text not null,
                tags text not null,
                created_at text not null,
                app text not null
            );

            create virtual table if not exists context_fts using fts5(
                title, body, people, tags,
                content='context_items',
                content_rowid='id'
            );

            create table if not exists reminders (
                id integer primary key,
                text text not null,
                due_hint text not null,
                created_at text default current_timestamp
            );

            create table if not exists audit_events (
                id integer primary key,
                request_id text not null,
                permission text not null,
                tool text not null,
                decision text not null,
                created_at text default current_timestamp
            );

            create trigger if not exists context_ai after insert on context_items begin
                insert into context_fts(rowid, title, body, people, tags)
                values (new.id, new.title, new.body, new.people, new.tags);
            end;
            """
        )
        self.conn.commit()

    def add_context(self, item: ContextItem) -> None:
        self.conn.execute(
            """
            insert into context_items(source, title, body, kind, people, tags, created_at, app)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.source,
                item.title,
                item.body,
                item.kind,
                ", ".join(item.people),
                ", ".join(item.tags),
                item.created_at,
                item.app,
            ),
        )
        self.conn.commit()

    def count_context(self) -> int:
        return int(self.conn.execute("select count(*) from context_items").fetchone()[0])

    def search(self, query: str, limit: int = 5) -> list[dict]:
        tokens = [
            token.strip(".,:;!?()[]{}'").replace('"', "")
            for token in query.split()
            if len(token.strip(".,:;!?()[]{}'")) > 1
        ]
        normalized = " OR ".join(tokens) if tokens else query
        try:
            rows = self.conn.execute(
                """
                select c.*, bm25(context_fts) as score
                from context_fts
                join context_items c on c.id = context_fts.rowid
                where context_fts match ?
                order by score
                limit ?
                """,
                (normalized, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
        if not rows:
            rows = self._substring_search(tokens or [query], limit)
        return [dict(row) for row in rows]

    def _substring_search(self, tokens: list[str], limit: int) -> list[sqlite3.Row]:
        clauses = [
            "lower(title || ' ' || body || ' ' || people || ' ' || tags) like lower(?)"
            for _ in tokens
        ]
        params = [f"%{token}%" for token in tokens]
        return self.conn.execute(
            f"""
            select *
            from context_items
            where {' or '.join(clauses)}
            order by created_at desc
            limit ?
            """,
            (*params, limit),
        ).fetchall()

    def create_reminder(self, text: str, due_hint: str) -> dict:
        cursor = self.conn.execute(
            "insert into reminders(text, due_hint) values (?, ?)",
            (text, due_hint),
        )
        self.conn.commit()
        return {"id": cursor.lastrowid, "text": text, "due_hint": due_hint}

    def audit(self, request_id: str, permission: str, tool: str, decision: str) -> None:
        self.conn.execute(
            "insert into audit_events(request_id, permission, tool, decision) values (?, ?, ?, ?)",
            (request_id, permission, tool, decision),
        )
        self.conn.commit()

    def recent_audit(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute(
            "select permission, tool, decision, created_at from audit_events order by id desc limit ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
