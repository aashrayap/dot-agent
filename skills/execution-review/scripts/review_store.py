#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from review_schema import DB_PATH, HERMES_FINDINGS_PATH, HISTORY_PATH, STATE_ROOT, ensure_state_layout

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS normalized_sessions (
    session_id TEXT NOT NULL,
    runtime TEXT NOT NULL,
    identity TEXT NOT NULL,
    cwd TEXT,
    started_at TEXT,
    ended_at TEXT,
    wall_seconds INTEGER DEFAULT 0,
    model TEXT,
    entrypoint TEXT,
    user_messages INTEGER DEFAULT 0,
    assistant_messages INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    edits INTEGER DEFAULT 0,
    verifications INTEGER DEFAULT 0,
    exec_failures INTEGER DEFAULT 0,
    subagent_count INTEGER DEFAULT 0,
    first_user_message TEXT,
    final_response_excerpt TEXT,
    payload_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (runtime, session_id)
);

CREATE TABLE IF NOT EXISTS review_runs (
    review_id TEXT PRIMARY KEY,
    window TEXT NOT NULL,
    runtime TEXT NOT NULL,
    created_at TEXT NOT NULL,
    report_path TEXT,
    history_json TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    ensure_state_layout()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn


def upsert_normalized_sessions(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    conn = connect()
    try:
        conn.executemany(
            """
            INSERT INTO normalized_sessions (
                session_id, runtime, identity, cwd, started_at, ended_at, wall_seconds,
                model, entrypoint, user_messages, assistant_messages, total_messages,
                edits, verifications, exec_failures, subagent_count,
                first_user_message, final_response_excerpt, payload_json, updated_at
            ) VALUES (
                :session_id, :runtime, :identity, :cwd, :started_at, :ended_at, :wall_seconds,
                :model, :entrypoint, :user_messages, :assistant_messages, :total_messages,
                :edits, :verifications, :exec_failures, :subagent_count,
                :first_user_message, :final_response_excerpt, :payload_json, :updated_at
            )
            ON CONFLICT(runtime, session_id) DO UPDATE SET
                identity=excluded.identity,
                cwd=excluded.cwd,
                started_at=excluded.started_at,
                ended_at=excluded.ended_at,
                wall_seconds=excluded.wall_seconds,
                model=excluded.model,
                entrypoint=excluded.entrypoint,
                user_messages=excluded.user_messages,
                assistant_messages=excluded.assistant_messages,
                total_messages=excluded.total_messages,
                edits=excluded.edits,
                verifications=excluded.verifications,
                exec_failures=excluded.exec_failures,
                subagent_count=excluded.subagent_count,
                first_user_message=excluded.first_user_message,
                final_response_excerpt=excluded.final_response_excerpt,
                payload_json=excluded.payload_json,
                updated_at=excluded.updated_at
            """,
            [
                {
                    "session_id": record["session_id"],
                    "runtime": record["runtime"],
                    "identity": record.get("identity", "default"),
                    "cwd": record.get("cwd"),
                    "started_at": record.get("started_at"),
                    "ended_at": record.get("ended_at"),
                    "wall_seconds": int(record.get("wall_seconds") or 0),
                    "model": record.get("model"),
                    "entrypoint": record.get("entrypoint"),
                    "user_messages": int(record.get("user_messages") or 0),
                    "assistant_messages": int(record.get("assistant_messages") or 0),
                    "total_messages": int(record.get("total_messages") or 0),
                    "edits": int(record.get("edits") or 0),
                    "verifications": int(record.get("verifications") or 0),
                    "exec_failures": int(record.get("exec_failures") or 0),
                    "subagent_count": int(record.get("subagent_count") or 0),
                    "first_user_message": record.get("first_user_message"),
                    "final_response_excerpt": record.get("final_response_excerpt"),
                    "payload_json": json.dumps(record, ensure_ascii=False),
                    "updated_at": record.get("updated_at") or record.get("ended_at") or record.get("started_at"),
                }
                for record in records
            ],
        )
        conn.commit()
    finally:
        conn.close()


def append_history_entry(entry: dict[str, Any]) -> None:
    ensure_state_layout()
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")


def record_review_run(
    *,
    review_id: str,
    window: str,
    runtime: str,
    created_at: str,
    report_path: str | None,
    history_entry: dict[str, Any],
) -> None:
    conn = connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO review_runs (
                review_id, window, runtime, created_at, report_path, history_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                window,
                runtime,
                created_at,
                report_path,
                json.dumps(history_entry, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    append_history_entry(history_entry)


def load_matching_hermes_findings(window: str, runtime: str) -> list[dict[str, Any]]:
    if not HERMES_FINDINGS_PATH.exists():
        return []
    matches: list[dict[str, Any]] = []
    with HERMES_FINDINGS_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if payload.get("window") != window:
                continue
            finding_runtime = payload.get("runtime", "all")
            if runtime != "all" and finding_runtime not in {"all", runtime}:
                continue
            matches.append(payload)
    return matches


def load_recent_history(limit: int = 20) -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    entries: list[dict[str, Any]] = []
    with HISTORY_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entries.append(json.loads(raw_line))
            except json.JSONDecodeError:
                continue
    return entries[-limit:]


def report_output_path(slug: str) -> Path:
    ensure_state_layout()
    return STATE_ROOT / "reports" / f"{slug}.md"
