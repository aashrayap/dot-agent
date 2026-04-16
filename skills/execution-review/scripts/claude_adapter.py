#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from review_schema import (
    build_response_fit,
    classify_command_text,
    excerpt,
    format_seconds,
    resolve_identity,
    to_dt,
    iso,
    utc_now,
)

CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_HOME / "projects"
SKILL_RE = re.compile(r"(?<!\w)\$([a-z0-9][a-z0-9-]*)")

READ_TOOL_NAMES = {"Read", "Grep", "Glob"}
EDIT_TOOL_NAMES = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SEARCH_TOOL_NAMES = {"WebSearch", "WebFetch"}
AGENT_TOOL_NAMES = {"Agent"}


def _extract_message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts: list[str] = []
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                parts.append(str(item.get("text", "")).strip())
    return " ".join(part for part in parts if part)


def _session_files(window_start) -> list[Path]:
    if not PROJECTS_DIR.exists():
        return []
    seen: set[Path] = set()
    files: list[Path] = []
    for project_dir in sorted(path for path in PROJECTS_DIR.iterdir() if path.is_dir()):
        index_path = project_dir / "sessions-index.json"
        if index_path.exists():
            try:
                payload = json.loads(index_path.read_text())
            except (OSError, json.JSONDecodeError):
                payload = {}
            for entry in payload.get("entries") or []:
                full_path = Path(entry.get("fullPath", "")).expanduser()
                if not full_path.is_file():
                    continue
                modified = to_dt(entry.get("modified"))
                if modified is None and entry.get("fileMtime"):
                    modified = to_dt(float(entry["fileMtime"]) / 1000.0)
                if modified is not None and modified < window_start:
                    continue
                resolved = full_path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                files.append(resolved)

        for session_path in sorted(project_dir.glob("*.jsonl")):
            resolved = session_path.resolve()
            if resolved in seen:
                continue
            if to_dt(session_path.stat().st_mtime) and to_dt(session_path.stat().st_mtime) < window_start:
                continue
            seen.add(resolved)
            files.append(resolved)
    return files


def _normalize_tool_categories(tool_counts: Counter[str]) -> dict[str, int]:
    categories = {"read": 0, "edit": 0, "exec": 0, "search": 0, "agent": 0, "other": 0}
    for name, count in tool_counts.items():
        if name in READ_TOOL_NAMES:
            categories["read"] += count
        elif name in EDIT_TOOL_NAMES:
            categories["edit"] += count
        elif name == "Bash":
            categories["exec"] += count
        elif name in SEARCH_TOOL_NAMES:
            categories["search"] += count
        elif name in AGENT_TOOL_NAMES:
            categories["agent"] += count
        else:
            categories["other"] += count
    return categories


def parse_claude_session(path: Path) -> dict[str, Any] | None:
    start_dt = None
    end_dt = None
    session_id = path.stem
    permission_mode = None
    cwd = None
    git_branch = None
    entrypoint = None
    model = None
    tool_counts: Counter[str] = Counter()
    skill_mentions: Counter[str] = Counter()
    user_texts: list[str] = []
    final_response_excerpt = ""
    input_tokens = 0
    output_tokens = 0
    cache_read_tokens = 0
    cache_create_tokens = 0
    assistant_messages = 0
    exec_failures = 0
    edits = 0
    verifications = 0
    subagent_count = 0
    pending_tool_uses: dict[str, dict[str, Any]] = {}

    try:
        handle = path.open()
    except OSError:
        return None

    with handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            event_dt = to_dt(event.get("timestamp"))
            if event_dt is not None:
                if start_dt is None or event_dt < start_dt:
                    start_dt = event_dt
                if end_dt is None or event_dt > end_dt:
                    end_dt = event_dt

            session_id = event.get("sessionId") or session_id
            cwd = event.get("cwd") or cwd
            git_branch = event.get("gitBranch") or git_branch
            entrypoint = event.get("entrypoint") or entrypoint

            event_type = event.get("type")
            if event_type == "permission-mode":
                permission_mode = event.get("permissionMode") or permission_mode
                continue

            if event_type == "assistant":
                assistant_messages += 1
                message = event.get("message") or {}
                model = message.get("model") or model
                content = message.get("content") or []
                text_parts: list[str] = []
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type == "text":
                        text_parts.append(str(item.get("text", "")).strip())
                    elif item_type == "tool_use":
                        tool_id = item.get("id")
                        name = item.get("name") or "unknown"
                        tool_counts[name] += 1
                        if name in EDIT_TOOL_NAMES:
                            edits += 1
                        if name in AGENT_TOOL_NAMES:
                            subagent_count += 1
                        pending_tool_uses[tool_id] = {
                            "name": name,
                            "command": ((item.get("input") or {}).get("command") or ""),
                        }
                        if name == "Bash":
                            classified = classify_command_text(((item.get("input") or {}).get("command") or ""))
                            if classified["verify"]:
                                verifications += 1
                if text_parts:
                    final_response_excerpt = " ".join(part for part in text_parts if part)

                usage = message.get("usage") or {}
                input_tokens += int(usage.get("input_tokens") or 0)
                output_tokens += int(usage.get("output_tokens") or 0)
                cache_read_tokens += int(usage.get("cache_read_input_tokens") or 0)
                cache_create_tokens += int(usage.get("cache_creation_input_tokens") or 0)
                continue

            if event_type == "user":
                message = event.get("message") or {}
                content = message.get("content")
                content_items = content if isinstance(content, list) else []
                if event.get("toolUseResult") is not None or any(
                    isinstance(item, dict) and item.get("type") == "tool_result" for item in content_items
                ):
                    for item in content_items:
                        if not isinstance(item, dict) or item.get("type") != "tool_result":
                            continue
                        call = pending_tool_uses.get(item.get("tool_use_id")) or {}
                        if call.get("name") == "Bash" and item.get("is_error"):
                            exec_failures += 1
                    continue

                text = _extract_message_text(content)
                if text:
                    user_texts.append(text)
                    for name in SKILL_RE.findall(text.lower()):
                        skill_mentions[name] += 1
                continue

    if start_dt is None:
        try:
            start_dt = to_dt(path.stat().st_mtime)
        except OSError:
            start_dt = None
    if end_dt is None:
        end_dt = start_dt

    if not user_texts and not assistant_messages:
        return None

    first_user = user_texts[0] if user_texts else ""
    identity = resolve_identity(cwd)
    total_messages = len(user_texts) + assistant_messages
    return {
        "session_id": session_id,
        "runtime": "claude",
        "identity": identity,
        "cwd": cwd,
        "git_branch": git_branch,
        "git_remote": None,
        "started_at": iso(start_dt),
        "ended_at": iso(end_dt),
        "updated_at": iso(utc_now()),
        "wall_seconds": max(0, int((end_dt - start_dt).total_seconds())) if start_dt and end_dt else 0,
        "wall_human": format_seconds(max(0, int((end_dt - start_dt).total_seconds())) if start_dt and end_dt else 0),
        "model": model,
        "entrypoint": entrypoint,
        "reasoning_effort": None,
        "approval_mode": None,
        "sandbox_policy": None,
        "permission_mode": permission_mode,
        "user_messages": len(user_texts),
        "assistant_messages": assistant_messages,
        "total_messages": total_messages,
        "commentary_messages": 0,
        "final_messages": assistant_messages,
        "tool_calls": _normalize_tool_categories(tool_counts),
        "tool_counts": dict(tool_counts),
        "edits": edits,
        "verifications": verifications,
        "exec_failures": exec_failures,
        "subagent_count": subagent_count,
        "skill_mentions": dict(skill_mentions),
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "cache_read": cache_read_tokens,
            "cache_create": cache_create_tokens,
            "total": input_tokens + output_tokens + cache_read_tokens + cache_create_tokens,
        },
        "first_user_message": excerpt(first_user, 280),
        "final_response_excerpt": excerpt(final_response_excerpt, 420),
        "response_fit": build_response_fit(
            first_user_message=first_user,
            final_response_excerpt=final_response_excerpt,
            user_messages=user_texts,
            assistant_messages=assistant_messages,
            commentary_messages=0,
            final_messages=assistant_messages,
        ),
        "signals": {
            "edited": edits > 0,
            "verified": verifications > 0,
            "edit_without_verification": edits > 0 and verifications == 0,
            "had_failures": exec_failures > 0,
        },
        "source_ref": str(path),
        "label": excerpt(first_user or session_id, 120),
    }


def fetch_claude_sessions(*, window_hours: float, session_ids: list[str] | None = None) -> list[dict[str, Any]]:
    window_start = utc_now()
    if window_hours is not None:
        from datetime import timedelta

        window_start = utc_now() - timedelta(hours=window_hours)
    if session_ids:
        candidates: list[Path] = []
        for session_id in session_ids:
            for path in PROJECTS_DIR.rglob(f"{session_id}.jsonl"):
                candidates.append(path)
    else:
        candidates = _session_files(window_start)

    sessions: list[dict[str, Any]] = []
    seen_ids: set[tuple[str, str]] = set()
    for path in candidates:
        session = parse_claude_session(path)
        if not session:
            continue
        key = (session["runtime"], session["session_id"])
        if key in seen_ids:
            continue
        seen_ids.add(key)
        sessions.append(session)
    return sessions


def load_claude_session(session_id: str) -> dict[str, Any] | None:
    sessions = fetch_claude_sessions(window_hours=24 * 365 * 3, session_ids=[session_id])
    return sessions[0] if sessions else None
