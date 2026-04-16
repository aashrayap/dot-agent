#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from codex_sessions import (
    connect_state_db,
    fetch_spawn_counts,
    select_threads,
    summarize_thread,
)
from review_schema import (
    build_response_fit,
    excerpt,
    format_seconds,
    iso,
    resolve_identity,
    utc_now,
)

def _categorize_codex_summary(summary: dict[str, Any]) -> dict[str, int]:
    accounted = (
        int(summary.get("read_commands") or 0)
        + int(summary.get("apply_patches") or 0)
        + int(summary.get("exec_commands") or 0)
        + int(summary.get("web_search_calls") or 0)
        + int(summary.get("spawned_threads") or 0)
    )
    other = max(int(summary.get("function_calls") or 0) - accounted, 0)
    return {
        "read": int(summary.get("read_commands") or 0),
        "edit": int(summary.get("apply_patches") or 0),
        "exec": int(summary.get("exec_commands") or 0),
        "search": int(summary.get("web_search_calls") or 0),
        "agent": int(summary.get("spawned_threads") or 0),
        "other": other,
    }


def _normalize_codex_summary(summary: dict[str, Any], *, tokens_used: int | None = None) -> dict[str, Any]:
    timeline = summary.get("timeline") or []
    user_messages = [item.get("text", "") for item in timeline if item.get("kind") == "user"]
    assistant_messages = [item.get("text", "") for item in timeline if str(item.get("kind", "")).startswith("agent_")]
    final_messages = [item.get("text", "") for item in timeline if item.get("kind") == "agent_final"]
    first_user = summary.get("first_user_message") or (user_messages[0] if user_messages else "")
    final_excerpt = final_messages[-1] if final_messages else (assistant_messages[-1] if assistant_messages else "")
    started_at = summary.get("started_at") or summary.get("created_at")
    ended_at = summary.get("ended_at") or summary.get("updated_at")
    identity = resolve_identity(summary.get("cwd"))

    return {
        "session_id": summary["id"],
        "runtime": "codex",
        "identity": identity,
        "cwd": summary.get("cwd"),
        "git_branch": summary.get("git_branch"),
        "git_remote": summary.get("git_remote"),
        "started_at": started_at,
        "ended_at": ended_at,
        "updated_at": iso(utc_now()),
        "wall_seconds": int(summary.get("wall_seconds") or 0),
        "wall_human": summary.get("wall_human") or format_seconds(summary.get("wall_seconds")),
        "model": summary.get("model"),
        "entrypoint": None,
        "reasoning_effort": summary.get("reasoning_effort"),
        "approval_mode": summary.get("approval_mode"),
        "sandbox_policy": summary.get("sandbox_policy"),
        "permission_mode": None,
        "user_messages": int(summary.get("user_messages") or 0),
        "assistant_messages": int(summary.get("agent_messages") or 0),
        "total_messages": int(summary.get("user_messages") or 0) + int(summary.get("agent_messages") or 0),
        "commentary_messages": int(summary.get("commentary_messages") or 0),
        "final_messages": int(summary.get("final_messages") or 0),
        "tool_calls": _categorize_codex_summary(summary),
        "tool_counts": summary.get("tool_counts") or {},
        "edits": int(summary.get("apply_patches") or 0),
        "verifications": int(summary.get("verification_commands") or 0),
        "exec_failures": int(summary.get("exec_failures") or 0),
        "subagent_count": int(summary.get("spawned_threads") or 0),
        "skill_mentions": summary.get("skill_mentions") or {},
        "tokens": {
            "input": None,
            "output": None,
            "cache_read": None,
            "cache_create": None,
            "total": tokens_used,
        },
        "first_user_message": excerpt(first_user, 280),
        "final_response_excerpt": excerpt(final_excerpt, 420),
        "response_fit": build_response_fit(
            first_user_message=first_user,
            final_response_excerpt=final_excerpt,
            user_messages=user_messages,
            assistant_messages=int(summary.get("agent_messages") or 0),
            commentary_messages=int(summary.get("commentary_messages") or 0),
            final_messages=int(summary.get("final_messages") or 0),
        ),
        "signals": summary.get("signals") or {},
        "source_ref": summary.get("rollout_path"),
        "label": summary.get("label"),
    }


def fetch_codex_sessions(
    *,
    window_hours: float | None = None,
    cwd: str | None = None,
    thread_ids: list[str] | None = None,
    include_subthreads: bool = False,
) -> list[dict[str, Any]]:
    conn = connect_state_db()
    try:
        rows = select_threads(
            conn,
            window_hours=window_hours,
            cwd=cwd,
            thread_ids=thread_ids,
            include_subthreads=include_subthreads,
        )
        spawn_counts = fetch_spawn_counts(conn)
    finally:
        conn.close()

    normalized: list[dict[str, Any]] = []
    for row in rows:
        summary = summarize_thread(
            row,
            spawn_count=spawn_counts.get(row["id"], 0),
            include_timeline=True,
        )
        summary["git_branch"] = row.get("git_branch")
        summary["git_remote"] = row.get("git_origin_url")
        normalized.append(_normalize_codex_summary(summary, tokens_used=row.get("tokens_used")))
    return normalized


def load_codex_session(session_id: str, *, include_subthreads: bool = False) -> dict[str, Any] | None:
    sessions = fetch_codex_sessions(
        thread_ids=[session_id],
        include_subthreads=include_subthreads,
    )
    return sessions[0] if sessions else None
