#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
fetch-last-day-sessions.py

Deterministic data collection for the /daily-review skill. Produces the
backbone that the skill's LLM synthesis layer consumes — nothing more.

Walks ~/.claude/projects/, finds every top-level session JSONL whose file
mtime falls inside the last N hours, and extracts a merged timeline of
"turns" across all sessions. Emits a compact JSON document with three
sections:

  day        — day-level totals (span, active time, agent/human latencies)
  sessions   — one-row-per-session index, enough to route drill-down
  turns      — merged, chronologically-sorted turn timeline

A "turn" is one human prompt + the agent's full response cycle (all
tool-use iterations until the next human prompt). Turns are the unit of
analysis for the final timeline chart, project clustering, multitasking
detection, and re-prompt pattern detection.

Deep per-session detail (full messages, per-tool durations, subagent
trees, error text) is deferred to a separate inspect-session script and
called on demand during the skill's fan-out phase.

Usage:
    ./fetch-last-day-sessions.py [--hours 24] [--idle-threshold 300]
                                 [--projects-dir PATH] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ---------- configuration ----------

DEFAULT_HOURS = 24.0
DEFAULT_IDLE_THRESHOLD_SECONDS = 300  # gaps > this before a human turn are "idle", not "think"
PROMPT_HEAD_CHARS = 120

# Re-prompt heuristics (flags only — final judgment is LLM, not script)
SHORT_PROMPT_CHAR_LIMIT = 50
SHORT_PROMPT_MIN_PRIOR_AGENT_SECONDS = 30
RAPID_FOLLOWUP_SECONDS = 10
CORRECTION_RE = re.compile(
    r"^\s*("
    r"no\b|nope\b|wrong\b|actually\b|"
    r"that'?s\s+not|that\s+is\s+not|"
    r"i\s+meant|i\s+said|"
    r"try\s+(again|instead)|instead\b|should\s+be|"
    r"not\s+(quite|that|what)|"
    r"wait\b|hmm\b|hm\b|ugh\b|"
    r"revert\b|rollback\b|undo\b"
    r")",
    re.IGNORECASE,
)

# User-role events that are actually system-generated IDE/harness notices,
# not human prompts. These should be classified as agent events so they
# don't pollute the turn timeline.
SYSTEM_USER_MESSAGE_RES = [
    re.compile(r"^\s*<ide_opened_file>", re.IGNORECASE),
    re.compile(r"^\s*<ide_selection>", re.IGNORECASE),
    re.compile(r"^\s*<local-command-caveat>", re.IGNORECASE),
    re.compile(r"^\s*<system-reminder>", re.IGNORECASE),
]


# ---------- small helpers ----------


def parse_ts(s: Any) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def unslug_project(slug: str) -> str:
    if slug.startswith("-"):
        return "/" + slug[1:].replace("-", "/")
    return slug


def extract_text(node: Any) -> str:
    """Flatten message.content into plain text (string or list of blocks)."""
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
        return " ".join(p for p in out if p)
    return ""


def is_human_prompt(ev: dict) -> bool:
    """A real human prompt — NOT a tool_result relay or system-generated notice.

    Tool results are delivered to the model as ``type: user`` messages whose
    content is a list of ``tool_result`` blocks — those belong to the agent's
    response cycle. IDE notices (file-opened, selection) and system reminders
    also come through with ``type: user`` but represent harness activity, not
    human input.
    """
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


def merge_intervals(intervals: list[tuple[datetime, datetime]]) -> float:
    if not intervals:
        return 0.0
    sorted_ivs = sorted(intervals, key=lambda x: x[0])
    merged: list[list[datetime]] = [list(sorted_ivs[0])]
    for start, end in sorted_ivs[1:]:
        if start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1][1] = end
        else:
            merged.append([start, end])
    return sum((e - s).total_seconds() for s, e in merged)


def count_subagents_in_dir(session_dir: Path) -> int:
    sub = session_dir / "subagents"
    if not sub.is_dir():
        return 0
    return sum(1 for p in sub.glob("agent-*.jsonl"))


# ---------- core: parse a single session into turns ----------


def parse_session(path: Path, idle_threshold: int) -> tuple[dict, list[dict]]:
    """Parse one session JSONL into (session_meta, turns).

    Walk events in timestamp order. Every inter-event gap is attributed
    to whichever side acted NEXT, but capped at ``idle_threshold`` — gaps
    above the cap are "idle" and drop out of both human_think_seconds and
    agent_seconds. A turn that goes dormant (agent gap > threshold with
    no human re-engagement) freezes at its last active timestamp; any
    trailing orphan agent events after the dormancy are ignored, so stray
    session-resume events can't balloon a turn's wall-clock span.
    """
    session_id: str | None = None
    cwd: str | None = None
    git_branch: str | None = None
    version: str | None = None

    events: list[dict] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                events.append(ev)
    except FileNotFoundError:
        return ({}, [])

    for ev in events:
        if session_id is None and ev.get("sessionId"):
            session_id = ev["sessionId"]
        if cwd is None and ev.get("cwd"):
            cwd = ev["cwd"]
        if git_branch is None and ev.get("gitBranch"):
            git_branch = ev["gitBranch"]
        if version is None and ev.get("version"):
            version = ev["version"]

    def event_ts(ev: dict) -> datetime:
        ts = parse_ts(ev.get("timestamp"))
        return ts or datetime.min.replace(tzinfo=timezone.utc)

    events.sort(key=event_ts)

    turns: list[dict] = []
    current: dict | None = None
    current_dormant = False
    prev_ts: datetime | None = None
    turn_idx = 0

    for ev in events:
        ts = parse_ts(ev.get("timestamp"))
        if ts is None:
            continue

        raw_delta = (ts - prev_ts).total_seconds() if prev_ts else 0.0
        if raw_delta < 0:
            raw_delta = 0.0

        if is_human_prompt(ev):
            # Close previous turn (agent_seconds already accumulated).
            if current is not None:
                turns.append(current)

            if prev_ts is None:
                human_think = 0
                idle_before = 0
            elif raw_delta <= idle_threshold:
                human_think = int(raw_delta)
                idle_before = 0
            else:
                human_think = idle_threshold
                idle_before = int(raw_delta - idle_threshold)

            prompt_text = extract_text(ev.get("message")).strip()
            current = {
                "turn_id": f"{session_id}#{turn_idx}",
                "session_id": session_id,
                "turn_index": turn_idx,
                "started_at_dt": ts,
                "ended_at_dt": ts,
                "human_think_seconds": human_think,
                "idle_before_seconds": idle_before,
                "agent_seconds": 0,
                "human_prompt_chars": len(prompt_text),
                "human_prompt_head": prompt_text[:PROMPT_HEAD_CHARS],
                "tool_count": 0,
                "tool_names_set": set(),
                "subagents_spawned": 0,
                "had_tool_error": False,
            }
            current_dormant = False
            turn_idx += 1
            prev_ts = ts
            continue

        # Agent event.
        if current is None:
            # Pre-first-turn noise (session-start hooks, ide opens, etc.).
            prev_ts = ts
            continue

        if current_dormant:
            # Turn already frozen. Ignore stray agent events so dead sessions
            # don't spawn 20-hour phantom turns.
            prev_ts = ts
            continue

        if raw_delta > idle_threshold:
            # Agent went silent for too long — freeze this turn and ignore
            # anything further inside it.
            current_dormant = True
            prev_ts = ts
            continue

        current["agent_seconds"] += int(raw_delta)
        current["ended_at_dt"] = ts

        etype = ev.get("type")
        if etype == "assistant":
            msg = ev.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        name = block.get("name", "unknown")
                        current["tool_count"] += 1
                        current["tool_names_set"].add(name)
                        if name == "Agent":
                            current["subagents_spawned"] += 1
        elif etype == "user":
            msg = ev.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        if block.get("is_error"):
                            current["had_tool_error"] = True

        prev_ts = ts

    if current is not None:
        turns.append(current)

    for t in turns:
        t["tool_names"] = sorted(t.pop("tool_names_set"))

    session_meta = {
        "session_id": session_id,
        "jsonl_path": str(path),
        "version": version,
        "project": cwd or unslug_project(path.parent.name),
        "git_branch": git_branch,
        "turn_count": len(turns),
        "subagent_count": count_subagents_in_dir(path.with_suffix("")),
    }
    if turns:
        session_meta["started_at_dt"] = turns[0]["started_at_dt"]
        session_meta["ended_at_dt"] = turns[-1]["ended_at_dt"]

    return (session_meta, turns)


# ---------- cross-session analytics ----------


def compute_parallel_turns(all_turns: list[dict]) -> None:
    """Fill turn["parallel_turns"] with turn_ids of other-session turns
    whose interval overlaps this one.
    """
    sorted_turns = sorted(all_turns, key=lambda t: t["started_at_dt"])
    for t in sorted_turns:
        t["parallel_turns"] = []
    for i, t in enumerate(sorted_turns):
        t_end = t["ended_at_dt"]
        for j in range(i + 1, len(sorted_turns)):
            u = sorted_turns[j]
            if u["started_at_dt"] >= t_end:
                break
            if u["session_id"] != t["session_id"]:
                t["parallel_turns"].append(u["turn_id"])
                u["parallel_turns"].append(t["turn_id"])


def compute_reprompt_signals(turns_by_session: dict[str, list[dict]]) -> None:
    """Flag each turn with heuristic signals (not conclusions).

    Signals: after_tool_error, short_prompt, rapid_followup, correction_phrase.
    """
    for session_turns in turns_by_session.values():
        session_turns.sort(key=lambda t: t["turn_index"])
        for i, t in enumerate(session_turns):
            signals: list[str] = []
            if i > 0:
                prev = session_turns[i - 1]
                if prev.get("had_tool_error"):
                    signals.append("after_tool_error")
                if (
                    t["human_prompt_chars"] < SHORT_PROMPT_CHAR_LIMIT
                    and prev.get("agent_seconds", 0) > SHORT_PROMPT_MIN_PRIOR_AGENT_SECONDS
                ):
                    signals.append("short_prompt")
                if 0 < t["human_think_seconds"] < RAPID_FOLLOWUP_SECONDS:
                    signals.append("rapid_followup")
                if CORRECTION_RE.match(t.get("human_prompt_head") or ""):
                    signals.append("correction_phrase")
            t["reprompt_signals"] = signals


# ---------- top-level orchestration ----------


def find_recent_session_files(projects_dir: Path, hours: float) -> list[Path]:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    out: list[Path] = []
    if not projects_dir.is_dir():
        return out
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for jf in project_dir.glob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(jf.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if mtime >= cutoff:
                out.append(jf)
    return out


def serialize_turn(t: dict) -> dict:
    return {
        "turn_id": t["turn_id"],
        "session_id": t["session_id"],
        "turn_index": t["turn_index"],
        "project": t["project"],
        "git_branch": t.get("git_branch"),
        "started_at": t["started_at_dt"].isoformat(),
        "ended_at": t["ended_at_dt"].isoformat(),
        "agent_seconds": t["agent_seconds"],
        "human_think_seconds": t["human_think_seconds"],
        "idle_before_seconds": t["idle_before_seconds"],
        "human_prompt_chars": t["human_prompt_chars"],
        "human_prompt_head": t["human_prompt_head"],
        "tool_count": t["tool_count"],
        "tool_names": t["tool_names"],
        "subagents_spawned": t["subagents_spawned"],
        "had_tool_error": t["had_tool_error"],
        "parallel_turns": t.get("parallel_turns", []),
        "reprompt_signals": t.get("reprompt_signals", []),
    }


def serialize_session(s: dict, session_turns: list[dict]) -> dict:
    agent_total = sum(t["agent_seconds"] for t in session_turns)
    human_total = sum(t["human_think_seconds"] for t in session_turns)
    idle_total = sum(t["idle_before_seconds"] for t in session_turns)
    parallel_peers: set[str] = set()
    for t in session_turns:
        for pid in t.get("parallel_turns", []):
            other_session = pid.split("#", 1)[0]
            if other_session != s["session_id"]:
                parallel_peers.add(other_session)
    started = s.get("started_at_dt")
    ended = s.get("ended_at_dt")
    return {
        "session_id": s["session_id"],
        "jsonl_path": s["jsonl_path"],
        "project": s["project"],
        "git_branch": s.get("git_branch"),
        "version": s.get("version"),
        "started_at": started.isoformat() if started else None,
        "ended_at": ended.isoformat() if ended else None,
        "wall_seconds": int((ended - started).total_seconds()) if started and ended else 0,
        "turn_count": s["turn_count"],
        "subagent_count": s["subagent_count"],
        "agent_seconds": agent_total,
        "human_seconds": human_total,
        "turn_idle_seconds": idle_total,
        "parallel_session_count": len(parallel_peers),
        "parallel_session_ids": sorted(parallel_peers),
    }


def build_day_totals(all_turns: list[dict], serialized_sessions: list[dict]) -> dict:
    if not all_turns:
        return {
            "first_prompt_at": None,
            "last_activity_at": None,
            "span_seconds": 0,
            "active_seconds": 0,
            "inactive_seconds": 0,
            "agent_seconds": 0,
            "human_seconds": 0,
            "turn_idle_seconds": 0,
            "summed_wall_seconds": 0,
        }
    first = min(t["started_at_dt"] for t in all_turns)
    last = max(t["ended_at_dt"] for t in all_turns)
    span = int((last - first).total_seconds())
    active = int(
        merge_intervals([(t["started_at_dt"], t["ended_at_dt"]) for t in all_turns])
    )
    return {
        "first_prompt_at": first.isoformat(),
        "last_activity_at": last.isoformat(),
        "span_seconds": span,
        "span_hours": round(span / 3600, 2),
        "active_seconds": active,
        "active_hours": round(active / 3600, 2),
        "inactive_seconds": max(0, span - active),
        "agent_seconds": sum(t["agent_seconds"] for t in all_turns),
        "human_seconds": sum(t["human_think_seconds"] for t in all_turns),
        "turn_idle_seconds": sum(t["idle_before_seconds"] for t in all_turns),
        "summed_wall_seconds": sum(s["wall_seconds"] for s in serialized_sessions),
    }


def build_graph(
    projects_dir: Path,
    hours: float,
    idle_threshold: int,
    session_id_filter: set[str] | None = None,
) -> dict:
    files = find_recent_session_files(projects_dir, hours)

    session_metas: list[dict] = []
    turns_by_session: dict[str, list[dict]] = {}
    all_turns: list[dict] = []

    for f in files:
        meta, turns = parse_session(f, idle_threshold)
        # Drop sessions that had no real human turns — they're either stubs
        # (IDE opened a file then the session closed) or contained only
        # system/harness events. They carry no signal and their null
        # started_at breaks downstream sorting.
        if not turns or meta.get("session_id") is None:
            continue
        for t in turns:
            t["project"] = meta.get("project")
            t["git_branch"] = meta.get("git_branch")
        session_metas.append(meta)
        turns_by_session[meta["session_id"]] = turns
        all_turns.extend(turns)

    # Parallel-turn detection is computed against the FULL window so a
    # filtered subagent query still sees accurate parallel peers — even
    # when the peer session is outside the filter set.
    compute_parallel_turns(all_turns)
    compute_reprompt_signals(turns_by_session)

    if session_id_filter is not None:
        session_metas = [m for m in session_metas if m["session_id"] in session_id_filter]
        all_turns = [t for t in all_turns if t["session_id"] in session_id_filter]

    all_turns.sort(key=lambda t: t["started_at_dt"])
    serialized_turns = [serialize_turn(t) for t in all_turns]

    serialized_sessions = [
        serialize_session(meta, turns_by_session[meta["session_id"]])
        for meta in session_metas
    ]
    serialized_sessions.sort(key=lambda s: s.get("started_at") or "")

    day = build_day_totals(all_turns, serialized_sessions)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": hours,
        "idle_threshold_seconds": idle_threshold,
        "projects_dir": str(projects_dir),
        "day": day,
        "sessions": serialized_sessions,
        "turns": serialized_turns,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=DEFAULT_HOURS)
    ap.add_argument(
        "--idle-threshold",
        type=int,
        default=DEFAULT_IDLE_THRESHOLD_SECONDS,
        help="Gaps before a human turn larger than this are idle, not think (seconds)",
    )
    ap.add_argument(
        "--projects-dir",
        type=Path,
        default=Path(
            os.environ.get("CLAUDE_PROJECTS_DIR", Path.home() / ".claude" / "projects")
        ),
    )
    ap.add_argument(
        "--session-ids",
        type=str,
        default=None,
        help=(
            "Comma-separated session IDs to include in output. The full window "
            "is still parsed so parallel-turn detection still references sibling "
            "sessions outside the filter."
        ),
    )
    ap.add_argument(
        "--project",
        type=str,
        default=None,
        help=(
            "Project slug (directory name under --projects-dir) to restrict "
            "output to. Combined with --session-ids via set intersection. "
            "The full window is still parsed for parallel-turn detection."
        ),
    )
    ap.add_argument(
        "--no-turns",
        action="store_true",
        help=(
            "Omit the per-turn list from the output. Use this from the main "
            "orchestrator when aggregating per-project totals — the `day` and "
            "`sessions` blocks are enough, and dropping `turns` keeps the "
            "orchestrator context lean. Subagents doing thread-level inspection "
            "should NOT pass this flag."
        ),
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    if not args.projects_dir.is_dir():
        print(f"error: projects dir not found: {args.projects_dir}", file=sys.stderr)
        return 1

    session_filter: set[str] | None = None
    if args.session_ids:
        session_filter = {sid.strip() for sid in args.session_ids.split(",") if sid.strip()}

    if args.project:
        project_dir = args.projects_dir / args.project
        if project_dir.is_dir():
            project_sids = {jf.stem for jf in project_dir.glob("*.jsonl")}
        else:
            project_sids = set()
        if session_filter is not None:
            session_filter = session_filter & project_sids
        else:
            session_filter = project_sids

    graph = build_graph(args.projects_dir, args.hours, args.idle_threshold, session_filter)
    if args.no_turns:
        graph.pop("turns", None)
    payload = json.dumps(graph, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(
            f"wrote {args.out} ({len(payload):,} bytes, "
            f"{len(graph['sessions'])} sessions, {len(graph['turns'])} turns)",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
