#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSIONS_DIR = CODEX_HOME / "sessions"

READ_PATTERNS = (
    "ls ",
    "find ",
    "rg ",
    "sed ",
    "cat ",
    "head ",
    "tail ",
    "wc ",
    "git status",
    "git diff",
    "git log",
    "git show",
    "sqlite3 ",
    "jq ",
)

VERIFY_PATTERNS = (
    "pytest",
    "py.test",
    "ruff",
    "mypy",
    "tox",
    "npx vitest",
    "vitest",
    "jest",
    "playwright",
    "npm test",
    "pnpm test",
    "yarn test",
    "npm run lint",
    "pnpm lint",
    "yarn lint",
    "go test",
    "cargo test",
    "cargo clippy",
    "bundle exec rspec",
    "rspec",
    "phpunit",
    "swift test",
    "xcodebuild test",
    "gradlew test",
    "mix test",
    "deno test",
)

SKILL_RE = re.compile(r"(?<!\w)\$([a-z0-9][a-z0-9-]*)")


def parse_window(spec: str) -> float:
    raw = spec.strip().lower()
    if raw in {"day", "daily"}:
        return 24.0
    if raw in {"week", "weekly"}:
        return 24.0 * 7
    if raw.endswith("h"):
        return float(raw[:-1])
    if raw.endswith("d"):
        return float(raw[:-1]) * 24.0
    if raw.endswith("w"):
        return float(raw[:-1]) * 24.0 * 7
    return float(raw)


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def local_day(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone().date().isoformat()


def format_seconds(seconds: float | int | None) -> str:
    total = int(round(seconds or 0))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def excerpt(text: str | None, limit: int = 140) -> str:
    value = normalize_ws(text or "")
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def extract_text(value: Any) -> str:
    parts: list[str] = []

    def visit(node: Any) -> None:
        if node is None:
            return
        if isinstance(node, str):
            if node.strip():
                parts.append(node.strip())
            return
        if isinstance(node, list):
            for item in node:
                visit(item)
            return
        if not isinstance(node, dict):
            return

        preferred = ("text", "output_text", "content", "message", "input")
        for key in preferred:
            if key in node:
                visit(node[key])

    visit(value)
    return normalize_ws(" ".join(parts))


def parse_source(raw_source: str | None) -> dict[str, Any]:
    if not raw_source:
        return {"kind": "top_level", "raw": ""}
    raw = raw_source.strip()
    if not raw.startswith("{"):
        return {"kind": "top_level", "raw": raw}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"kind": "top_level", "raw": raw}

    spawn = ((data.get("subagent") or {}).get("thread_spawn")) or {}
    if spawn:
        return {
            "kind": "subagent",
            "raw": raw,
            "parent_thread_id": spawn.get("parent_thread_id"),
            "depth": spawn.get("depth"),
            "agent_nickname": spawn.get("agent_nickname"),
            "agent_role": spawn.get("agent_role"),
        }
    return {"kind": "structured", "raw": raw, "data": data}


def resolve_state_db() -> Path:
    override = os.environ.get("CODEX_STATE_DB")
    if override:
        return Path(override).expanduser()
    candidates = sorted(CODEX_HOME.glob("state_*.sqlite"))
    if candidates:
        return candidates[-1]
    raise FileNotFoundError(f"no state_*.sqlite found under {CODEX_HOME}")


def connect_state_db() -> sqlite3.Connection:
    db = resolve_state_db()
    uri = f"file:{db}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def find_rollout_path(thread_id: str, rollout_path: str | None) -> Path | None:
    if rollout_path:
        candidate = Path(rollout_path).expanduser()
        if candidate.is_file():
            return candidate

    matches = sorted(SESSIONS_DIR.rglob(f"*{thread_id}.jsonl"))
    return matches[-1] if matches else None


def select_threads(
    conn: sqlite3.Connection,
    *,
    window_hours: float | None = None,
    cwd: str | None = None,
    thread_ids: list[str] | None = None,
    include_subthreads: bool = False,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if thread_ids:
        placeholders = ",".join("?" for _ in thread_ids)
        where.append(f"id IN ({placeholders})")
        params.extend(thread_ids)
    elif window_hours is not None:
        cutoff = int((utc_now() - timedelta(hours=window_hours)).timestamp())
        where.append("updated_at >= ?")
        params.append(cutoff)

    if cwd:
        where.append("cwd = ?")
        params.append(cwd)

    sql = """
        SELECT
            id,
            rollout_path,
            created_at,
            updated_at,
            source,
            model_provider,
            cwd,
            title,
            sandbox_policy,
            approval_mode,
            tokens_used,
            git_sha,
            git_branch,
            git_origin_url,
            cli_version,
            first_user_message,
            agent_nickname,
            agent_role,
            memory_mode,
            model,
            reasoning_effort,
            agent_path
        FROM threads
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at ASC"

    rows = [dict(row) for row in conn.execute(sql, params)]
    filtered: list[dict[str, Any]] = []
    for row in rows:
        source_info = parse_source(row.get("source"))
        row["source_info"] = source_info
        if source_info["kind"] == "subagent" and not include_subthreads:
            continue
        filtered.append(row)
    return filtered


def fetch_spawn_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    query = """
        SELECT parent_thread_id, COUNT(*) AS child_count
        FROM thread_spawn_edges
        GROUP BY parent_thread_id
    """
    for row in conn.execute(query):
        counts[row["parent_thread_id"]] = int(row["child_count"])
    return counts


def classify_command(cmd: str) -> dict[str, bool]:
    normalized = normalize_ws(cmd).lower()
    read_like = any(normalized.startswith(pattern) for pattern in READ_PATTERNS)
    verify_like = any(pattern in normalized for pattern in VERIFY_PATTERNS)
    return {"read": read_like, "verify": verify_like}


def summarize_thread(
    row: dict[str, Any],
    *,
    spawn_count: int = 0,
    include_timeline: bool = False,
) -> dict[str, Any]:
    rollout_path = find_rollout_path(row["id"], row.get("rollout_path"))
    start_dt = None
    end_dt = None
    cmd_calls: dict[str, dict[str, Any]] = {}
    tool_counts: Counter[str] = Counter()
    skill_mentions: Counter[str] = Counter()
    timeline: list[dict[str, Any]] = []
    command_events: list[dict[str, Any]] = []

    metrics: dict[str, Any] = {
        "user_messages": 0,
        "agent_messages": 0,
        "commentary_messages": 0,
        "final_messages": 0,
        "reasoning_items": 0,
        "function_calls": 0,
        "function_call_outputs": 0,
        "web_search_calls": 0,
        "web_search_events": 0,
        "exec_commands": 0,
        "exec_failures": 0,
        "exec_duration_ms": 0,
        "read_commands": 0,
        "verification_commands": 0,
        "apply_patches": 0,
        "parallel_calls": 0,
        "parallel_tool_uses": 0,
        "token_events": 0,
    }

    first_user_text = row.get("first_user_message") or ""

    if rollout_path and rollout_path.is_file():
        with rollout_path.open() as handle:
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

                event_type = event.get("type")
                payload = event.get("payload") or {}

                if event_type == "session_meta":
                    session_ts = to_dt((payload or {}).get("timestamp"))
                    if session_ts is not None:
                        if start_dt is None or session_ts < start_dt:
                            start_dt = session_ts
                        if end_dt is None or session_ts > end_dt:
                            end_dt = session_ts
                    continue

                if event_type == "event_msg":
                    kind = payload.get("type")
                    if kind == "user_message":
                        metrics["user_messages"] += 1
                        text = extract_text(payload)
                        if text:
                            if not first_user_text:
                                first_user_text = text
                            for name in SKILL_RE.findall(text.lower()):
                                skill_mentions[name] += 1
                        if include_timeline:
                            timeline.append(
                                {
                                    "timestamp": iso(event_dt),
                                    "kind": "user",
                                    "text": excerpt(text, 220),
                                }
                            )
                    elif kind == "agent_message":
                        metrics["agent_messages"] += 1
                        phase = payload.get("phase") or "unknown"
                        if phase == "commentary":
                            metrics["commentary_messages"] += 1
                        else:
                            metrics["final_messages"] += 1
                        if include_timeline:
                            timeline.append(
                                {
                                    "timestamp": iso(event_dt),
                                    "kind": f"agent_{phase}",
                                    "text": excerpt(extract_text(payload), 220),
                                }
                            )
                    elif kind == "exec_command_end":
                        metrics["exec_commands"] += 1
                        exit_code = payload.get("exit_code", 0)
                        duration = payload.get("duration") or {}
                        duration_ms = int(duration.get("secs", 0) * 1000 + duration.get("nanos", 0) / 1_000_000)
                        metrics["exec_duration_ms"] += duration_ms
                        if exit_code:
                            metrics["exec_failures"] += 1
                        call_id = payload.get("call_id")
                        call = cmd_calls.get(call_id, {})
                        command_events.append(
                            {
                                "timestamp": iso(event_dt),
                                "call_id": call_id,
                                "cmd": call.get("cmd", ""),
                                "workdir": call.get("workdir"),
                                "exit_code": exit_code,
                                "duration_ms": duration_ms,
                            }
                        )
                        if include_timeline:
                            timeline.append(
                                {
                                    "timestamp": iso(event_dt),
                                    "kind": "exec_command",
                                    "cmd": excerpt(call.get("cmd", ""), 180),
                                    "exit_code": exit_code,
                                    "duration_ms": duration_ms,
                                }
                            )
                    elif kind == "web_search_end":
                        metrics["web_search_events"] += 1
                    elif kind == "token_count":
                        metrics["token_events"] += 1
                    continue

                if event_type != "response_item":
                    continue

                kind = payload.get("type")
                if kind == "function_call":
                    metrics["function_calls"] += 1
                    tool_name = payload.get("name") or "unknown"
                    tool_counts[tool_name] += 1
                    args_text = payload.get("arguments") or ""
                    if tool_name == "apply_patch":
                        metrics["apply_patches"] += 1
                    if tool_name == "multi_tool_use.parallel":
                        metrics["parallel_calls"] += 1
                        try:
                            parsed = json.loads(args_text)
                        except json.JSONDecodeError:
                            parsed = {}
                        metrics["parallel_tool_uses"] += len(parsed.get("tool_uses") or [])
                    if tool_name == "exec_command":
                        try:
                            parsed = json.loads(args_text)
                        except json.JSONDecodeError:
                            parsed = {"cmd": args_text}
                        cmd = parsed.get("cmd", "")
                        cmd_calls[payload.get("call_id")] = {
                            "cmd": cmd,
                            "workdir": parsed.get("workdir"),
                        }
                        command_kind = classify_command(cmd)
                        if command_kind["read"]:
                            metrics["read_commands"] += 1
                        if command_kind["verify"]:
                            metrics["verification_commands"] += 1
                    continue

                if kind == "function_call_output":
                    metrics["function_call_outputs"] += 1
                    continue

                if kind == "web_search_call":
                    metrics["web_search_calls"] += 1
                    continue

                if kind == "reasoning":
                    metrics["reasoning_items"] += 1
                    continue

    if start_dt is None:
        start_dt = datetime.fromtimestamp(row["created_at"], tz=timezone.utc)
    if end_dt is None:
        end_dt = datetime.fromtimestamp(row["updated_at"], tz=timezone.utc)

    wall_seconds = max(0, int((end_dt - start_dt).total_seconds()))
    label_source = first_user_text or row.get("title") or row["id"]
    source_info = row.get("source_info") or {}

    summary = {
        "id": row["id"],
        "label": excerpt(label_source, 120),
        "first_user_message": excerpt(first_user_text or row.get("first_user_message"), 220),
        "cwd": row["cwd"],
        "source": row.get("source"),
        "source_kind": source_info.get("kind"),
        "source_parent_thread_id": source_info.get("parent_thread_id"),
        "agent_role": source_info.get("agent_role") or row.get("agent_role"),
        "agent_nickname": source_info.get("agent_nickname") or row.get("agent_nickname"),
        "created_at": iso(datetime.fromtimestamp(row["created_at"], tz=timezone.utc)),
        "updated_at": iso(datetime.fromtimestamp(row["updated_at"], tz=timezone.utc)),
        "started_at": iso(start_dt),
        "ended_at": iso(end_dt),
        "day": local_day(start_dt),
        "wall_seconds": wall_seconds,
        "wall_human": format_seconds(wall_seconds),
        "model": row.get("model"),
        "reasoning_effort": row.get("reasoning_effort"),
        "approval_mode": row.get("approval_mode"),
        "sandbox_policy": row.get("sandbox_policy"),
        "tool_counts": dict(tool_counts),
        "skill_mentions": dict(skill_mentions),
        "spawned_threads": spawn_count,
        "rollout_path": str(rollout_path) if rollout_path else None,
        **metrics,
    }

    summary["signals"] = {
        "edited": summary["apply_patches"] > 0,
        "verified": summary["verification_commands"] > 0,
        "edit_without_verification": summary["apply_patches"] > 0 and summary["verification_commands"] == 0,
        "had_failures": summary["exec_failures"] > 0,
        "heavy_read_before_action": summary["read_commands"] >= 8 and summary["apply_patches"] == 0,
        "spawn_heavy": summary["spawned_threads"] >= 3,
    }

    if include_timeline:
        summary["timeline"] = timeline
        summary["commands"] = command_events

    return summary


def build_aggregate(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    if not summaries:
        return {
            "summary": {
                "threads": 0,
                "unique_cwds": 0,
                "wall_seconds": 0,
                "wall_human": "0s",
                "context_switches": 0,
            },
            "days": [],
            "cwds": [],
            "threads": [],
        }

    ordered = sorted(summaries, key=lambda item: item["started_at"] or item["created_at"] or "")
    total_wall_seconds = sum(item["wall_seconds"] for item in ordered)
    first_started = ordered[0]["started_at"]
    last_activity = max(item["ended_at"] or item["updated_at"] for item in ordered)
    first_started_dt = to_dt(first_started)
    last_activity_dt = to_dt(last_activity)
    calendar_span_seconds = 0
    if first_started_dt is not None and last_activity_dt is not None:
        calendar_span_seconds = max(0, int((last_activity_dt - first_started_dt).total_seconds()))

    summary: dict[str, Any] = {
        "threads": len(ordered),
        "unique_cwds": len({item["cwd"] for item in ordered}),
        "wall_seconds": total_wall_seconds,
        "wall_human": format_seconds(total_wall_seconds),
        "session_wall_seconds": total_wall_seconds,
        "session_wall_human": format_seconds(total_wall_seconds),
        "calendar_span_seconds": calendar_span_seconds,
        "calendar_span_human": format_seconds(calendar_span_seconds),
        "first_started_at": first_started,
        "last_activity_at": last_activity,
        "context_switches": 0,
        "apply_patches": sum(item["apply_patches"] for item in ordered),
        "verification_commands": sum(item["verification_commands"] for item in ordered),
        "exec_failures": sum(item["exec_failures"] for item in ordered),
        "function_calls": sum(item["function_calls"] for item in ordered),
        "web_search_calls": sum(item["web_search_calls"] for item in ordered),
        "spawned_threads": sum(item["spawned_threads"] for item in ordered),
        "edit_without_verification_threads": sum(1 for item in ordered if item["signals"]["edit_without_verification"]),
    }

    previous_cwd = None
    day_map: dict[str, dict[str, Any]] = {}
    cwd_map: dict[str, dict[str, Any]] = {}

    for item in ordered:
        if previous_cwd is not None and item["cwd"] != previous_cwd:
            summary["context_switches"] += 1
        previous_cwd = item["cwd"]

        day_key = item["day"] or "unknown"
        day_entry = day_map.setdefault(
            day_key,
            {
                "day": day_key,
                "threads": 0,
                "unique_cwds": set(),
                "wall_seconds": 0,
                "wall_human": "0s",
                "session_wall_seconds": 0,
                "session_wall_human": "0s",
                "calendar_span_seconds": 0,
                "calendar_span_human": "0s",
                "context_switches": 0,
                "apply_patches": 0,
                "verification_commands": 0,
                "exec_failures": 0,
                "edit_without_verification_threads": 0,
                "first_started_at": item["started_at"],
                "last_activity_at": item["ended_at"] or item["updated_at"],
            },
        )
        day_entry["threads"] += 1
        day_entry["unique_cwds"].add(item["cwd"])
        day_entry["wall_seconds"] += item["wall_seconds"]
        day_entry["session_wall_seconds"] += item["wall_seconds"]
        day_entry["apply_patches"] += item["apply_patches"]
        day_entry["verification_commands"] += item["verification_commands"]
        day_entry["exec_failures"] += item["exec_failures"]
        day_entry["edit_without_verification_threads"] += int(item["signals"]["edit_without_verification"])
        if item["started_at"] and item["started_at"] < day_entry["first_started_at"]:
            day_entry["first_started_at"] = item["started_at"]
        if (item["ended_at"] or item["updated_at"]) > day_entry["last_activity_at"]:
            day_entry["last_activity_at"] = item["ended_at"] or item["updated_at"]

        cwd_entry = cwd_map.setdefault(
            item["cwd"],
            {
                "cwd": item["cwd"],
                "threads": 0,
                "wall_seconds": 0,
                "wall_human": "0s",
                "apply_patches": 0,
                "verification_commands": 0,
                "exec_failures": 0,
            },
        )
        cwd_entry["threads"] += 1
        cwd_entry["wall_seconds"] += item["wall_seconds"]
        cwd_entry["apply_patches"] += item["apply_patches"]
        cwd_entry["verification_commands"] += item["verification_commands"]
        cwd_entry["exec_failures"] += item["exec_failures"]

    for item in ordered:
        day_key = item["day"] or "unknown"
        day_entry = day_map[day_key]
        prev = day_entry.get("_prev_cwd")
        if prev is not None and item["cwd"] != prev:
            day_entry["context_switches"] += 1
        day_entry["_prev_cwd"] = item["cwd"]

    days: list[dict[str, Any]] = []
    for key in sorted(day_map):
        day_entry = day_map[key]
        day_entry["unique_cwds"] = len(day_entry["unique_cwds"])
        day_entry["wall_human"] = format_seconds(day_entry["wall_seconds"])
        day_entry["session_wall_human"] = format_seconds(day_entry["session_wall_seconds"])
        day_first_dt = to_dt(day_entry["first_started_at"])
        day_last_dt = to_dt(day_entry["last_activity_at"])
        if day_first_dt is not None and day_last_dt is not None:
            day_entry["calendar_span_seconds"] = max(0, int((day_last_dt - day_first_dt).total_seconds()))
        day_entry["calendar_span_human"] = format_seconds(day_entry["calendar_span_seconds"])
        day_entry.pop("_prev_cwd", None)
        days.append(day_entry)

    cwds: list[dict[str, Any]] = []
    for key in sorted(cwd_map, key=lambda cwd: (-cwd_map[cwd]["wall_seconds"], cwd)):
        entry = cwd_map[key]
        entry["wall_human"] = format_seconds(entry["wall_seconds"])
        cwds.append(entry)

    return {"summary": summary, "days": days, "cwds": cwds, "threads": ordered}
