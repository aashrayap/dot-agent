#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", Path.home() / ".dot-agent")).expanduser()
STATE_HOME = Path(os.environ.get("DOT_AGENT_STATE_HOME", DOT_AGENT_HOME / "state")).expanduser()
ROADMAP_FILE = STATE_HOME / "collab" / "roadmap.md"
HERMES_FINDINGS = STATE_HOME / "collab" / "execution-reviews" / "hermes-findings.jsonl"
EXEC_REVIEW_SCRIPTS = DOT_AGENT_HOME / "skills" / "execution-review" / "scripts"

if str(EXEC_REVIEW_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EXEC_REVIEW_SCRIPTS))

try:
    from claude_adapter import fetch_claude_sessions
    from codex_adapter import fetch_codex_sessions
    from review_schema import format_seconds, to_dt
except Exception as exc:  # pragma: no cover - reported through CLI
    fetch_claude_sessions = None  # type: ignore[assignment]
    fetch_codex_sessions = None  # type: ignore[assignment]
    format_seconds = None  # type: ignore[assignment]
    to_dt = None  # type: ignore[assignment]
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+")
SKILL_RE = re.compile(r"(?<!\w)\$([a-z0-9][a-z0-9-]*)")


@dataclass
class RoadmapRow:
    project: str
    status: str
    task: str
    link: str
    notes: str


@dataclass
class PRSignal:
    repo: str
    state: str
    source: str = "gh"
    open_count: int = 0
    recent_merged_count: int = 0
    closed_unmerged_count: int = 0
    attention: str = ""
    note: str = ""


@dataclass
class Workstream:
    name: str
    roadmap: bool = False
    sessions: list[dict[str, Any]] = field(default_factory=list)
    subcategories: Counter[str] = field(default_factory=Counter)
    runtime_counts: Counter[str] = field(default_factory=Counter)
    band_counts: Counter[str] = field(default_factory=Counter)
    repos: set[Path] = field(default_factory=set)
    roadmap_repos: set[Path] = field(default_factory=set)
    roadmap_rows: list[RoadmapRow] = field(default_factory=list)
    pr_signals: list[PRSignal] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a concise morning recent-work summary.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Local date for the morning packet.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--skip-prs", action="store_true", help="Skip GitHub PR lookup.")
    parser.add_argument("--repo-limit", type=int, default=8, help="Max recently touched git repos to check for PRs.")
    parser.add_argument("--pr-limit", type=int, default=3, help="Max PRs to show per repo.")
    parser.add_argument("--session-limit", type=int, default=80, help="Max recent sessions to consider.")
    return parser.parse_args()


def local_tz():
    return datetime.now().astimezone().tzinfo


def parse_local_date(raw: str) -> date:
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid --date {raw!r}; expected YYYY-MM-DD") from exc


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def split_table_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def read_roadmap_rows(path: Path = ROADMAP_FILE) -> list[RoadmapRow]:
    text = read_text(path)
    if not text:
        return []
    rows: list[RoadmapRow] = []
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if section != "Active Projects" or not line.startswith("|"):
            continue
        parts = split_table_row(line)
        if len(parts) < 5 or parts[0] in {"Project", "---------"} or parts[2] == "-":
            continue
        rows.append(RoadmapRow(parts[0], parts[1], parts[2], parts[3], parts[4]))
    return rows


def normalize_label(text: str | None, limit_words: int = 9) -> str:
    raw = URL_RE.sub(" ", TAG_RE.sub(" ", text or ""))
    raw = raw.replace("\\n", " ")
    raw = re.sub(r"[/#`*_{}\[\]():;,]+", " ", raw)
    words = [word for word in raw.split() if word and not word.isdigit()]
    if not words:
        return "general"
    return " ".join(words[:limit_words]).strip() or "general"


def git_root(cwd: str | None) -> Path | None:
    if not cwd:
        return None
    path = Path(cwd).expanduser()
    if not path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    return Path(root) if root else None


def repo_from_link(link: str) -> Path | None:
    if not link or link == "-" or URL_RE.match(link):
        return None
    path = Path(link).expanduser()
    if not path.exists():
        return None
    root = git_root(str(path))
    return root


def workstream_from_session(session: dict[str, Any], roadmap_projects: set[str]) -> str:
    cwd = str(session.get("cwd") or "")
    root = git_root(cwd)
    candidates = []
    if root:
        if root == DOT_AGENT_HOME:
            candidates.append("dot-agent")
        candidates.append(root.name)
    elif cwd:
        candidates.append(Path(cwd).name)
    label = str(session.get("label") or session.get("first_user_message") or "")
    lowered_label = label.lower()
    for project in sorted(roadmap_projects, key=len, reverse=True):
        if project and project.lower() in lowered_label:
            return project
    for candidate in candidates:
        if candidate:
            return candidate
    return "general"


def session_local_day(session: dict[str, Any]) -> date | None:
    if to_dt is None:
        return None
    value = session.get("ended_at") or session.get("started_at")
    dt = to_dt(value)
    if dt is None:
        return None
    return dt.astimezone(local_tz()).date()


def band_for_day(day: date | None, today: date) -> str | None:
    if day is None:
        return None
    delta = (today - day).days
    if delta < 0:
        return None
    if delta == 0:
        return "today"
    if delta == 1:
        return "primary"
    if delta in {2, 3}:
        return "secondary"
    if 4 <= delta <= 8:
        return "tertiary"
    return None


def load_sessions(today: date, limit: int) -> list[dict[str, Any]]:
    if IMPORT_ERROR is not None or fetch_codex_sessions is None or fetch_claude_sessions is None:
        raise SystemExit(f"ERROR: failed to import execution-review adapters: {IMPORT_ERROR}")
    # 9 days catches today plus yesterday + 2 prior + 5 prior days across timezone edges.
    records: list[dict[str, Any]] = []
    records.extend(fetch_codex_sessions(window_hours=24 * 9))
    records.extend(fetch_claude_sessions(window_hours=24 * 9))
    filtered = [record for record in records if band_for_day(session_local_day(record), today)]
    filtered.sort(key=lambda item: item.get("ended_at") or item.get("started_at") or "", reverse=True)
    return filtered[:limit]


def build_workstreams(
    sessions: list[dict[str, Any]],
    roadmap_rows: list[RoadmapRow],
    today: date,
) -> dict[str, Workstream]:
    roadmap_projects = {row.project for row in roadmap_rows if row.project and row.project != "-"}
    streams: dict[str, Workstream] = {}
    for row in roadmap_rows:
        stream = streams.setdefault(row.project, Workstream(row.project, roadmap=True))
        stream.roadmap = True
        stream.roadmap_rows.append(row)
        repo = repo_from_link(row.link)
        if repo:
            stream.roadmap_repos.add(repo)
            stream.repos.add(repo)

    for session in sessions:
        name = workstream_from_session(session, roadmap_projects)
        stream = streams.setdefault(name, Workstream(name))
        stream.sessions.append(session)
        stream.runtime_counts[str(session.get("runtime") or "unknown")] += 1
        stream.subcategories[normalize_label(session.get("label") or session.get("first_user_message"))] += 1
        band = band_for_day(session_local_day(session), today)
        if band:
            stream.band_counts[band] += 1
        root = git_root(session.get("cwd"))
        if root and not stream.roadmap_repos:
            stream.repos.add(root)
    return streams


def remote_repo(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    match = re.search(r"github.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", raw)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def gh_json(args: list[str], cwd: Path | None = None, timeout: int = 8) -> Any:
    result = subprocess.run(
        ["gh", *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip() or "gh command failed")
    return json.loads(result.stdout or "null")


def summarize_pr_signal(repo_name: str, rows: list[dict[str, Any]]) -> PRSignal:
    open_rows = [row for row in rows if str(row.get("state") or "").upper() == "OPEN"]
    merged_rows = [row for row in rows if row.get("mergedAt")]
    closed_unmerged_rows = [
        row
        for row in rows
        if str(row.get("state") or "").upper() == "CLOSED" and not row.get("mergedAt")
    ]
    attention = ""
    if open_rows:
        first = open_rows[0]
        review = str(first.get("reviewDecision") or "review ?").lower()
        attention = f"open PR #{first.get('number')}: {first.get('title')} ({review})"
    elif merged_rows:
        attention = "recent merged PR activity"
    state = "present" if open_rows or merged_rows or closed_unmerged_rows else "empty"
    return PRSignal(
        repo=repo_name,
        state=state,
        open_count=len(open_rows),
        recent_merged_count=len(merged_rows),
        closed_unmerged_count=len(closed_unmerged_rows),
        attention=attention,
        note="no recent PR signal" if state == "empty" else "",
    )


def fetch_repo_pr_signal(repo_root: Path, limit: int) -> tuple[Path, PRSignal | None]:
    repo_name = remote_repo(repo_root)
    if not repo_name:
        return repo_root, None
    try:
        rows = gh_json(
            [
                "pr",
                "list",
                "--repo",
                repo_name,
                "--state",
                "all",
                "--limit",
                str(limit),
                "--json",
                ",".join(
                    [
                        "number",
                        "title",
                        "state",
                        "url",
                        "updatedAt",
                        "headRefName",
                        "baseRefName",
                        "reviewDecision",
                        "mergedAt",
                        "closedAt",
                        "isDraft",
                    ]
                ),
            ],
            cwd=repo_root,
        )
    except Exception as exc:
        return repo_root, PRSignal(repo=repo_name, state="unavailable", note=str(exc))
    return repo_root, summarize_pr_signal(repo_name, rows)


def attach_prs(streams: dict[str, Workstream], repo_limit: int, pr_limit: int, skip: bool) -> list[str]:
    if skip:
        return ["Skipped: PR lookup disabled by --skip-prs."]
    if shutil.which("gh") is None:
        return ["Unavailable: gh not found."]
    repo_to_streams: dict[Path, list[Workstream]] = defaultdict(list)
    for stream in streams.values():
        if not stream.roadmap:
            continue
        for repo in stream.repos:
            repo_to_streams[repo].append(stream)
    repos = sorted(repo_to_streams, key=lambda path: str(path))[:repo_limit]
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=min(4, max(len(repos), 1))) as pool:
        futures = {pool.submit(fetch_repo_pr_signal, repo, pr_limit): repo for repo in repos}
        for future in as_completed(futures):
            repo, signal = future.result()
            if signal is None:
                continue
            if signal.state == "unavailable":
                errors.append(f"{repo.name}: {signal.note}")
            for stream in repo_to_streams.get(repo, []):
                stream.pr_signals.append(signal)
    return errors


def hermes_status(today: date) -> str:
    if not HERMES_FINDINGS.exists() or HERMES_FINDINGS.stat().st_size == 0:
        return "Hermes: no findings"
    count = 0
    titles: list[str] = []
    with HERMES_FINDINGS.open(encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            created = payload.get("created_at")
            dt = to_dt(created) if to_dt else None
            if dt is not None:
                local_day = dt.astimezone(local_tz()).date()
                if (today - local_day).days > 8:
                    continue
            count += 1
            title = str(payload.get("title") or payload.get("id") or "Hermes finding")
            if len(titles) < 2:
                titles.append(title)
    if count == 0:
        return "Hermes: no findings"
    suffix = f" ({'; '.join(titles)})" if titles else ""
    return f"Hermes: {count} finding(s){suffix}"


def total_wall_human(sessions: list[dict[str, Any]]) -> str:
    seconds = sum(int(item.get("wall_seconds") or 0) for item in sessions)
    if format_seconds is None:
        return f"{seconds}s"
    return format_seconds(seconds)


def total_wall_seconds(sessions: list[dict[str, Any]]) -> int:
    return sum(int(item.get("wall_seconds") or 0) for item in sessions)


def session_key(session: dict[str, Any]) -> str:
    return str(session.get("ended_at") or session.get("started_at") or "")


def session_has_unverified_edit(session: dict[str, Any]) -> bool:
    return int(session.get("edits") or 0) > 0 and int(session.get("verifications") or 0) == 0


def pr_open_count(stream: Workstream) -> int:
    return sum(signal.open_count for signal in stream.pr_signals)


DISPOSABLE_LABEL_PATTERNS = (
    "reply with exactly ok",
    "explain database connection pooling in one sentence",
    "codex-hook-smoke",
    "codex-global-hook-smoke",
    "codex-caveman",
    "tesy",
)


def is_disposable_stream(stream: Workstream) -> bool:
    haystack = " ".join(
        [
            stream.name,
            *(
                str(session.get("label") or session.get("first_user_message") or "")
                for session in stream.sessions
            ),
        ]
    ).lower()
    return any(pattern in haystack for pattern in DISPOSABLE_LABEL_PATTERNS)


def should_show_user_decides(stream: Workstream) -> bool:
    if stream.roadmap or not stream.sessions:
        return False
    if is_disposable_stream(stream):
        return bool(stream.band_counts.get("today") and len(stream.sessions) >= 2)
    if stream.band_counts.get("today") or stream.band_counts.get("primary"):
        return True
    if len(stream.sessions) >= 2:
        return True
    return total_wall_seconds(stream.sessions) >= 15 * 60


def stream_state(stream: Workstream) -> str:
    latest = max(stream.sessions, key=session_key) if stream.sessions else None
    edit_without_verify = any(session_has_unverified_edit(s) for s in stream.sessions)
    failures = sum(int(s.get("exec_failures") or 0) for s in stream.sessions)
    if not stream.roadmap:
        return "not on roadmap"
    if latest and session_has_unverified_edit(latest):
        return "open gate"
    if edit_without_verify:
        return "verification risk"
    if failures:
        return "rough edges"
    if stream.band_counts.get("primary") or stream.band_counts.get("today"):
        return "active"
    return "tracked"


def suggested_next(stream: Workstream) -> str:
    state = stream_state(stream)
    if state == "not on roadmap":
        return "user decides"
    if state == "open gate":
        return "verify gate"
    if state == "verification risk":
        return "check verification"
    if pr_open_count(stream):
        return "review PR signal"
    if stream.band_counts.get("primary") or stream.band_counts.get("today"):
        return "continue or park"
    return "keep visible"


def last_touched(stream: Workstream, today: date) -> str:
    days = [session_local_day(item) for item in stream.sessions]
    days = [day for day in days if day is not None]
    if not days:
        return "-"
    delta = (today - max(days)).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "yesterday"
    return f"{delta}d ago"


def evidence_cell(stream: Workstream) -> str:
    runtimes = ", ".join(f"{name}:{count}" for name, count in sorted(stream.runtime_counts.items()))
    wall = total_wall_human(stream.sessions)
    open_prs = pr_open_count(stream)
    pr_bit = f"; open PRs:{open_prs}" if open_prs else ""
    roadmap_bit = "; roadmap" if stream.roadmap else ""
    return f"{len(stream.sessions)} sessions ({runtimes}; {wall}){pr_bit}{roadmap_bit}"


def top_subcategory(stream: Workstream) -> str:
    if not stream.subcategories:
        if stream.roadmap_rows:
            return normalize_label(stream.roadmap_rows[0].task, 7)
        return "general"
    return stream.subcategories.most_common(1)[0][0]


def sorted_streams(streams: dict[str, Workstream]) -> list[Workstream]:
    def key(stream: Workstream) -> tuple[int, int, int, str]:
        priority = 0 if stream.band_counts.get("primary") else 1
        return (
            priority,
            -stream.band_counts.get("today", 0) - stream.band_counts.get("primary", 0),
            -len(stream.sessions),
            stream.name.lower(),
        )

    return sorted(streams.values(), key=key)


def markdown_table(rows: list[list[str]]) -> str:
    headers = ["Workstream", "Subcategory", "Evidence", "Last touched", "State", "Suggested next"]
    out = ["| " + " | ".join(headers) + " |", "|---|---|---|---|---|---|"]
    for row in rows:
        out.append("| " + " | ".join(cell.replace("|", "/") for cell in row) + " |")
    return "\n".join(out)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    today = parse_local_date(args.date)
    roadmap_rows = read_roadmap_rows()
    sessions = load_sessions(today, args.session_limit)
    streams = build_workstreams(sessions, roadmap_rows, today)
    pr_errors = attach_prs(streams, args.repo_limit, args.pr_limit, args.skip_prs)
    ordered = sorted_streams(streams)
    raw_user_decides = [stream for stream in ordered if stream.sessions and not stream.roadmap]
    user_decides = [stream for stream in raw_user_decides if should_show_user_decides(stream)]
    omitted_user_decides = len(raw_user_decides) - len(user_decides)
    visible_user_decides = {id(stream) for stream in user_decides}
    tracked = [stream for stream in ordered if stream.roadmap or id(stream) in visible_user_decides]
    open_gates = [
        stream
        for stream in tracked
        if stream_state(stream) in {"open gate", "verification risk", "rough edges"}
        or any(signal.state == "unavailable" for signal in stream.pr_signals)
    ]
    return {
        "date": today.isoformat(),
        "window": {
            "primary": "yesterday",
            "secondary": "2 prior days",
            "tertiary": "5 prior days",
        },
        "sessions": len(sessions),
        "roadmap_rows": [row.__dict__ for row in roadmap_rows],
        "streams": [
            {
                "workstream": stream.name,
                "subcategory": top_subcategory(stream),
                "evidence": evidence_cell(stream) if stream.sessions else "roadmap only",
                "last_touched": last_touched(stream, today),
                "state": stream_state(stream),
                "suggested_next": suggested_next(stream),
                "roadmap": stream.roadmap,
                "pr_signals": [signal.__dict__ for signal in stream.pr_signals],
            }
            for stream in tracked
        ],
        "user_decides": [
            {
                "workstream": stream.name,
                "subcategory": top_subcategory(stream),
                "evidence": evidence_cell(stream),
                "last_touched": last_touched(stream, today),
            }
            for stream in user_decides
        ],
        "omitted_user_decides": omitted_user_decides,
        "current_commitments": [
            f"{row.project}: {row.task} ({row.status})"
            for row in roadmap_rows
            if row.status.lower() in {"queued", "in progress", "review", "needs review", "waiting", "follow-up", "blocked"}
        ],
        "open_gates": [
            f"{stream.name}: {stream_state(stream)}"
            for stream in open_gates[:8]
        ],
        "hermes": hermes_status(today),
        "pr_errors": pr_errors,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    rows = [
        [
            item["workstream"],
            item["subcategory"],
            item["evidence"],
            item["last_touched"],
            item["state"],
            item["suggested_next"],
        ]
        for item in payload["streams"]
        if item["evidence"] != "roadmap only"
    ]
    lines: list[str] = []
    lines.append("## Date")
    lines.append(f"- {payload['date']}")
    lines.append("")
    lines.append("## Window")
    lines.append("- Primary: yesterday")
    lines.append("- Secondary: 2 prior days")
    lines.append("- Tertiary: 5 prior days")
    lines.append("")
    lines.append("## What you've been working on")
    lines.append(markdown_table(rows) if rows else "- No recent Codex or Claude work found in the morning window.")
    lines.append("")
    lines.append("## User Decides")
    if payload["user_decides"]:
        for item in payload["user_decides"][:8]:
            lines.append(f"- {item['workstream']}: {item['subcategory']} ({item['last_touched']}; {item['evidence']})")
    else:
        lines.append("- No untracked recent work found.")
    if payload.get("omitted_user_decides"):
        lines.append(f"- Omitted {payload['omitted_user_decides']} stale or disposable row(s).")
    lines.append("")
    lines.append("## Current commitments")
    if payload["current_commitments"]:
        lines.extend(f"- {item}" for item in payload["current_commitments"])
    else:
        lines.append("- No in-progress commitments found in roadmap.")
    lines.append("")
    lines.append("## Open gates")
    if payload["open_gates"]:
        lines.extend(f"- {item}" for item in payload["open_gates"])
    else:
        lines.append("- No obvious gates found from recent metadata.")
    lines.append("")
    lines.append("## Recent PRs")
    any_prs = False
    any_checked = False
    any_unavailable = False
    reported_global_pr_error = False
    for stream in payload["streams"]:
        signals = stream.get("pr_signals") or []
        actionable = [signal for signal in signals if signal.get("state") == "present"]
        unavailable = [signal for signal in signals if signal.get("state") == "unavailable"]
        empty = [signal for signal in signals if signal.get("state") == "empty"]
        if empty:
            any_checked = True
        if unavailable:
            any_unavailable = True
            lines.append(f"- {stream['workstream']}: PR lookup unavailable ({unavailable[0].get('note')})")
            continue
        if not actionable:
            continue
        any_checked = True
        any_prs = True
        open_count = sum(int(signal.get("open_count") or 0) for signal in actionable)
        merged_count = sum(int(signal.get("recent_merged_count") or 0) for signal in actionable)
        closed_count = sum(int(signal.get("closed_unmerged_count") or 0) for signal in actionable)
        attention = next((signal.get("attention") for signal in actionable if signal.get("attention")), "")
        bits = []
        if open_count:
            bits.append(f"{open_count} open")
        if merged_count:
            bits.append(f"{merged_count} recently merged")
        if closed_count:
            bits.append(f"{closed_count} closed unmerged")
        detail = "; ".join(bits) if bits else "recent PR activity"
        suffix = f"; {attention}" if attention else ""
        lines.append(f"- {stream['workstream']}: {detail}{suffix}")
    if not any_prs:
        if any_unavailable:
            pass
        elif any_checked:
            lines.append("- No open or recently updated PRs found for mapped GitHub repos.")
        elif payload["pr_errors"]:
            lines.append(f"- {payload['pr_errors'][0]}")
            reported_global_pr_error = True
        else:
            lines.append("- No mapped GitHub repos found for PR lookup.")
    if payload["pr_errors"]:
        for error in payload["pr_errors"][:4]:
            if not any_unavailable and not reported_global_pr_error:
                lines.append(f"  - PR check note: {error}")
    lines.append("")
    lines.append("## Hermes")
    lines.append(f"- {payload['hermes']}")
    lines.append("")
    lines.append("## Recommended focus")
    first = next((item for item in payload["streams"] if item["state"] != "not on roadmap"), None)
    if first:
        lines.append(f"- Consider carrying forward `{first['workstream']}`: {first['suggested_next']}.")
    else:
        lines.append("- Pick from `User Decides` before changing roadmap.")
    lines.append("")
    lines.append("## Decision prompt")
    lines.append("- Which stream should carry forward? I can then route selected roadmap changes through `focus` and create the approved working doc.")
    lines.append("")
    lines.append("## Roadmap mutations proposed")
    lines.append("- None until you select a stream.")
    lines.append("")
    lines.append("## Not changing unless approved")
    lines.append("- Roadmap rows, focus text, parked/completed status, and morning working docs.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    if args.format == "json":
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
