#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
inspect-session.py

Drill-down companion to fetch-last-day-sessions.py. Given one session
(by id or jsonl path), emits a detailed per-turn view that the /daily-review
skill's fan-out agents can use to reconstruct what the human was doing
in that session: full human messages, per-turn tool sequences with
durations and result previews, final assistant text per turn, and a
parallel breakdown of any subagents that session spawned.

Usage:
    ./inspect-session.py --session-id <uuid> [--out file.json]
    ./inspect-session.py --jsonl /path/to/<uuid>.jsonl [--out file.json]

Env overrides:
    CLAUDE_PROJECTS_DIR  defaults to ~/.claude/projects
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------- config ----------

DEFAULT_IDLE_THRESHOLD_SECONDS = 300

HUMAN_MSG_CHAR_LIMIT = 8000
ASSISTANT_MSG_CHAR_LIMIT = 3000
TOOL_INPUT_CHAR_LIMIT = 300
TOOL_RESULT_CHAR_LIMIT = 500
TOOL_ERROR_CHAR_LIMIT = 1500

SYSTEM_USER_MESSAGE_RES = [
    re.compile(r"^\s*<ide_opened_file>", re.IGNORECASE),
    re.compile(r"^\s*<ide_selection>", re.IGNORECASE),
    re.compile(r"^\s*<local-command-caveat>", re.IGNORECASE),
    re.compile(r"^\s*<system-reminder>", re.IGNORECASE),
]


# ---------- shared helpers (mirror fetch-last-day-sessions.py) ----------


def parse_ts(s: Any) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def extract_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if "content" in node:
            return extract_text(node["content"])
        if node.get("type") == "text":
            return node.get("text", "") or ""
        return ""
    if isinstance(node, list):
        out: list[str] = []
        for block in node:
            if isinstance(block, str):
                out.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                out.append(block.get("text", "") or "")
        return "\n".join(p for p in out if p)
    return ""


def is_human_prompt(ev: dict) -> bool:
    if ev.get("type") != "user":
        return False
    msg = ev.get("message") or {}
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                return False
    text = extract_text(msg).lstrip()
    if not text:
        return False
    for rx in SYSTEM_USER_MESSAGE_RES:
        if rx.match(text):
            return False
    return True


# ---------- tool input/result summarization ----------


def summarize_tool_input(name: str, inp: Any) -> str:
    """Short human-readable summary of a tool_use input."""
    if not isinstance(inp, dict):
        return str(inp)[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Bash":
        return (inp.get("command") or "")[:TOOL_INPUT_CHAR_LIMIT]
    if name in ("Read", "Write", "NotebookEdit"):
        return (inp.get("file_path") or inp.get("notebook_path") or "")[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Edit":
        fp = inp.get("file_path", "")
        old = (inp.get("old_string") or "").split("\n", 1)[0][:60]
        return f"{fp} :: {old}"[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Grep":
        pat = inp.get("pattern", "")
        path = inp.get("path", ".")
        glob = inp.get("glob") or inp.get("type") or ""
        return f"{pat!r} in {path} {glob}".strip()[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Glob":
        return (inp.get("pattern") or "")[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Agent":
        subtype = inp.get("subagent_type", "general-purpose")
        desc = inp.get("description", "")
        return f"[{subtype}] {desc}"[:TOOL_INPUT_CHAR_LIMIT]
    if name == "Skill":
        sk = inp.get("skill") or ""
        args = inp.get("args") or ""
        return f"/{sk} {args}".strip()[:TOOL_INPUT_CHAR_LIMIT]
    if name in ("TaskCreate", "TaskUpdate"):
        return (inp.get("task") or inp.get("description") or "")[:TOOL_INPUT_CHAR_LIMIT]
    if name == "WebFetch":
        return (inp.get("url") or "")[:TOOL_INPUT_CHAR_LIMIT]
    if name == "WebSearch":
        return (inp.get("query") or "")[:TOOL_INPUT_CHAR_LIMIT]
    # Generic fallback: first non-empty string value
    for k, v in inp.items():
        if isinstance(v, str) and v:
            return f"{k}={v}"[:TOOL_INPUT_CHAR_LIMIT]
    return ""


def extract_tool_result_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for b in content:
            if isinstance(b, str):
                parts.append(b)
            elif isinstance(b, dict) and b.get("type") == "text":
                parts.append(b.get("text", "") or "")
        return "\n".join(parts)
    return ""


# ---------- main walk ----------


def inspect_session_file(path: Path, idle_threshold: int) -> dict:
    """Parse one jsonl into a detailed per-turn view."""
    try:
        events: list[dict] = []
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        return {"error": f"file not found: {path}"}

    session_id: str | None = None
    cwd: str | None = None
    git_branch: str | None = None
    version: str | None = None
    for ev in events:
        session_id = session_id or ev.get("sessionId")
        cwd = cwd or ev.get("cwd")
        git_branch = git_branch or ev.get("gitBranch")
        version = version or ev.get("version")

    def event_ts_key(ev: dict) -> datetime:
        ts = parse_ts(ev.get("timestamp"))
        return ts or datetime.min.replace(tzinfo=timezone.utc)

    events.sort(key=event_ts_key)

    turns: list[dict] = []
    current: dict | None = None
    current_dormant = False
    prev_ts: datetime | None = None
    turn_idx = 0
    # tool_use_id -> (start_ts, name, input_summary) for cross-event matching
    tool_starts: dict[str, tuple[datetime, str, str]] = {}

    for ev in events:
        ts = parse_ts(ev.get("timestamp"))
        if ts is None:
            continue

        raw_delta = (ts - prev_ts).total_seconds() if prev_ts else 0.0
        if raw_delta < 0:
            raw_delta = 0.0

        if is_human_prompt(ev):
            if current is not None:
                turns.append(current)

            if prev_ts is None:
                think = 0
                idle = 0
            elif raw_delta <= idle_threshold:
                think = int(raw_delta)
                idle = 0
            else:
                think = idle_threshold
                idle = int(raw_delta - idle_threshold)

            prompt_text = extract_text(ev.get("message")).strip()
            current = {
                "turn_index": turn_idx,
                "started_at": ts.isoformat(),
                "ended_at": ts.isoformat(),
                "human_think_seconds": think,
                "idle_before_seconds": idle,
                "agent_seconds": 0,
                "human_message": prompt_text[:HUMAN_MSG_CHAR_LIMIT],
                "human_message_chars": len(prompt_text),
                "human_message_truncated": len(prompt_text) > HUMAN_MSG_CHAR_LIMIT,
                "tool_sequence": [],
                "tool_count": 0,
                "had_tool_error": False,
                "subagents_spawned": 0,
                "subagent_invocations": [],
                "final_assistant_text": "",
                "final_assistant_text_truncated": False,
            }
            current_dormant = False
            turn_idx += 1
            prev_ts = ts
            continue

        # Agent event.
        if current is None:
            prev_ts = ts
            continue
        if current_dormant:
            prev_ts = ts
            continue
        if raw_delta > idle_threshold:
            current_dormant = True
            prev_ts = ts
            continue

        current["agent_seconds"] += int(raw_delta)
        current["ended_at"] = ts.isoformat()

        etype = ev.get("type")
        if etype == "assistant":
            msg = ev.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                # Gather all text blocks from this message as the "final assistant text"
                # for the turn so far. We overwrite each time so the LAST assistant
                # message in the turn wins.
                text_parts: list[str] = []
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "text":
                        text_parts.append(block.get("text", "") or "")
                    elif btype == "tool_use":
                        tid = block.get("id") or ""
                        name = block.get("name", "unknown")
                        inp_summary = summarize_tool_input(name, block.get("input"))
                        tool_starts[tid] = (ts, name, inp_summary)
                        current["tool_sequence"].append(
                            {
                                "tool": name,
                                "tool_use_id": tid,
                                "started_at": ts.isoformat(),
                                "input_summary": inp_summary,
                                "duration_seconds": None,
                                "is_error": False,
                                "result_preview": None,
                            }
                        )
                        current["tool_count"] += 1
                        if name == "Agent":
                            current["subagents_spawned"] += 1
                            current["subagent_invocations"].append(
                                {
                                    "subagent_type": (block.get("input") or {}).get(
                                        "subagent_type", "general-purpose"
                                    ),
                                    "description": (block.get("input") or {}).get(
                                        "description", ""
                                    ),
                                    "tool_use_id": tid,
                                }
                            )
                if text_parts:
                    combined = "\n".join(p for p in text_parts if p)
                    current["final_assistant_text"] = combined[:ASSISTANT_MSG_CHAR_LIMIT]
                    current["final_assistant_text_truncated"] = (
                        len(combined) > ASSISTANT_MSG_CHAR_LIMIT
                    )
        elif etype == "user":
            msg = ev.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_result":
                        continue
                    tid = block.get("tool_use_id") or ""
                    is_err = bool(block.get("is_error"))
                    if is_err:
                        current["had_tool_error"] = True
                    result_text = extract_tool_result_text(block.get("content"))
                    limit = TOOL_ERROR_CHAR_LIMIT if is_err else TOOL_RESULT_CHAR_LIMIT
                    preview = result_text[:limit]

                    # Find the matching tool_use entry in the current turn's sequence
                    match = next(
                        (
                            t
                            for t in reversed(current["tool_sequence"])
                            if t["tool_use_id"] == tid
                        ),
                        None,
                    )
                    if match is not None:
                        start_info = tool_starts.get(tid)
                        if start_info is not None:
                            match["duration_seconds"] = round(
                                (ts - start_info[0]).total_seconds(), 2
                            )
                        match["is_error"] = is_err
                        match["result_preview"] = preview

        prev_ts = ts

    if current is not None:
        turns.append(current)

    # Session-level aggregates
    started_at = turns[0]["started_at"] if turns else None
    ended_at = turns[-1]["ended_at"] if turns else None
    wall = 0
    if turns:
        first = parse_ts(turns[0]["started_at"])
        last = parse_ts(turns[-1]["ended_at"])
        if first and last:
            wall = int((last - first).total_seconds())

    return {
        "session_id": session_id,
        "jsonl_path": str(path),
        "project": cwd,
        "git_branch": git_branch,
        "version": version,
        "started_at": started_at,
        "ended_at": ended_at,
        "wall_seconds": wall,
        "turn_count": len(turns),
        "agent_seconds": sum(t["agent_seconds"] for t in turns),
        "human_think_seconds": sum(t["human_think_seconds"] for t in turns),
        "idle_seconds": sum(t["idle_before_seconds"] for t in turns),
        "tool_error_count": sum(1 for t in turns if t["had_tool_error"]),
        "turns": turns,
    }


# ---------- subagent drill-down ----------


def inspect_subagents(session_dir: Path, idle_threshold: int) -> list[dict]:
    sub_dir = session_dir / "subagents"
    if not sub_dir.is_dir():
        return []
    out: list[dict] = []
    for jf in sorted(sub_dir.glob("agent-*.jsonl")):
        meta_path = jf.with_suffix(".meta.json")
        meta: dict[str, Any] | None = None
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                meta = None

        detail = inspect_session_file(jf, idle_threshold)

        tool_counts: dict[str, int] = {}
        for t in detail.get("turns", []):
            for entry in t.get("tool_sequence", []):
                tool_counts[entry["tool"]] = tool_counts.get(entry["tool"], 0) + 1

        final_text = ""
        if detail.get("turns"):
            final_text = detail["turns"][-1].get("final_assistant_text", "") or ""

        out.append(
            {
                "agent_id": jf.stem,
                "agent_type": (meta or {}).get("agentType"),
                "description": (meta or {}).get("description"),
                "jsonl_path": str(jf),
                "started_at": detail.get("started_at"),
                "ended_at": detail.get("ended_at"),
                "duration_seconds": detail.get("wall_seconds", 0),
                "turn_count": detail.get("turn_count", 0),
                "agent_seconds": detail.get("agent_seconds", 0),
                "tool_counts": tool_counts,
                "tool_error_count": detail.get("tool_error_count", 0),
                "final_assistant_text": final_text,
                "turns": detail.get("turns", []),
            }
        )
    return out


# ---------- session lookup ----------


def find_session_jsonl(projects_dir: Path, session_id: str) -> Path | None:
    for project in projects_dir.iterdir():
        if not project.is_dir():
            continue
        candidate = project / f"{session_id}.jsonl"
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--session-id", help="Session UUID to inspect")
    group.add_argument("--jsonl", type=Path, help="Direct path to the session jsonl")
    ap.add_argument(
        "--projects-dir",
        type=Path,
        default=Path(
            os.environ.get("CLAUDE_PROJECTS_DIR", Path.home() / ".claude" / "projects")
        ),
    )
    ap.add_argument(
        "--idle-threshold",
        type=int,
        default=DEFAULT_IDLE_THRESHOLD_SECONDS,
    )
    ap.add_argument(
        "--no-subagents",
        action="store_true",
        help="Skip parsing the subagents/ directory (smaller output)",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    if args.jsonl:
        path = args.jsonl
        if not path.exists():
            print(f"error: jsonl not found: {path}", file=sys.stderr)
            return 1
    else:
        path = find_session_jsonl(args.projects_dir, args.session_id)
        if path is None:
            print(
                f"error: session {args.session_id} not found under {args.projects_dir}",
                file=sys.stderr,
            )
            return 1

    detail = inspect_session_file(path, args.idle_threshold)
    if "error" in detail:
        print(f"error: {detail['error']}", file=sys.stderr)
        return 1

    if not args.no_subagents:
        session_dir = path.with_suffix("")
        detail["subagents"] = inspect_subagents(session_dir, args.idle_threshold)
    else:
        detail["subagents"] = []

    payload = json.dumps(detail, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(
            f"wrote {args.out} ({len(payload):,} bytes, "
            f"{detail['turn_count']} turns, {len(detail['subagents'])} subagents)",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
