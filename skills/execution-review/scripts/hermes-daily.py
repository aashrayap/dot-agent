#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from claude_adapter import fetch_claude_sessions
from codex_adapter import fetch_codex_sessions
from review_schema import (
    DOT_AGENT_HOME,
    HERMES_FINDINGS_PATH,
    aggregate_normalized_sessions,
    format_seconds,
    iso,
    parse_window,
    utc_now,
)
from review_store import upsert_normalized_sessions


STATE_HOME = Path(os.environ.get("DOT_AGENT_STATE_HOME", DOT_AGENT_HOME / "state")).expanduser()
HERMES_ROOT = STATE_HOME / "collab" / "hermes"
DAILY_DIR = HERMES_ROOT / "daily"
THESIS_PATH = HERMES_ROOT / "thesis.md"
DEFAULT_SCOPE_ROOTS = (
    DOT_AGENT_HOME,
    Path.home() / "Documents" / "2026" / "semi-stocks-2",
)

DEFAULT_THESIS = """# Hermes Thesis

Hermes watches `dot-agent` and `semi-stocks-2` for workflow drift, repeated loops, and non-forward-progress signals.

## Operating Thesis

Forward progress means scoped work moves toward a reviewable artifact, verified change, clearer decision, or explicit handoff. Repeated exploration, repeated topic restarts, edit-without-verification, and frequent context switching are loop risks.

## Human Review Contract

Hermes findings reach human review through the daily synthesis first. Background runs summarize review-worthy findings in the thread inbox. Morning sync shows only a tiny Hermes status line. Full forensic detail stays in execution-review.

## Mutation Boundary

Hermes may suggest actions. It does not mutate roadmap rows, focus text, parked/completed state, or daily-review closure.
"""

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "keep",
    "new",
    "of",
    "on",
    "or",
    "please",
    "the",
    "this",
    "to",
    "with",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the scoped Hermes daily workflow check.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--window", default="24h", help="day, week, raw hours, or suffixed values like 36h / 7d")
    parser.add_argument("--runtime", default="all", choices=["all", "codex", "claude"])
    parser.add_argument("--scope-root", action="append", default=[], help="Repo/workspace root to include. Repeatable.")
    parser.add_argument("--write", action="store_true", help="Write thesis, log, synthesis, and compatibility findings.")
    parser.add_argument("--no-compat-findings", action="store_true", help="Do not append review-worthy findings to hermes-findings.jsonl.")
    return parser.parse_args()


def parse_local_date(raw: str) -> str:
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid --date {raw!r}; expected YYYY-MM-DD") from exc


def resolve_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def scope_roots(raw_roots: list[str]) -> list[tuple[str, Path]]:
    roots = [Path(item).expanduser() for item in raw_roots] if raw_roots else list(DEFAULT_SCOPE_ROOTS)
    scoped: list[tuple[str, Path]] = []
    for root in roots:
        resolved = resolve_path(root)
        label = "dot-agent" if resolved == resolve_path(DOT_AGENT_HOME) else resolved.name
        scoped.append((label, resolved))
    return scoped


def scope_for_cwd(cwd: str | None, roots: list[tuple[str, Path]]) -> str | None:
    if not cwd:
        return None
    path = resolve_path(cwd)
    for label, root in roots:
        if path == root or root in path.parents:
            return label
    return None


def fetch_records(runtime: str, window_hours: float) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if runtime in {"all", "codex"}:
        records.extend(fetch_codex_sessions(window_hours=window_hours))
    if runtime in {"all", "claude"}:
        records.extend(fetch_claude_sessions(window_hours=window_hours))
    return records


def topic_key(session: dict[str, Any]) -> str:
    text = " ".join(
        str(session.get(key) or "")
        for key in ("label", "first_user_message", "final_response_excerpt")
    ).lower()
    words = [word for word in re.findall(r"[a-z0-9][a-z0-9-]+", text) if word not in STOPWORDS]
    if not words:
        return "general"
    return " ".join(words[:6])


def tool_total(session: dict[str, Any]) -> int:
    calls = session.get("tool_calls") or {}
    return sum(int(calls.get(key) or 0) for key in ("read", "search", "exec", "other"))


def session_digest(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime": session.get("runtime"),
        "session_id": session.get("session_id"),
        "scope": session.get("hermes_scope"),
        "cwd": session.get("cwd"),
        "started_at": session.get("started_at"),
        "ended_at": session.get("ended_at"),
        "wall_seconds": int(session.get("wall_seconds") or 0),
        "label": session.get("label"),
        "edits": int(session.get("edits") or 0),
        "verifications": int(session.get("verifications") or 0),
        "exec_failures": int(session.get("exec_failures") or 0),
        "tool_calls": session.get("tool_calls") or {},
        "signals": session.get("signals") or {},
        "topic": topic_key(session),
    }


def finding_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:48] or "finding"


def build_findings(payload: dict[str, Any], sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = payload.get("summary") or {}
    findings: list[dict[str, Any]] = []
    low_progress = [
        item
        for item in sessions
        if int(item.get("edits") or 0) == 0
        and int(item.get("verifications") or 0) == 0
        and int(item.get("exec_failures") or 0) == 0
        and tool_total(item) >= 8
    ]
    edit_without_verify = [
        item for item in sessions if int(item.get("edits") or 0) > 0 and int(item.get("verifications") or 0) == 0
    ]
    failures = [item for item in sessions if int(item.get("exec_failures") or 0) > 0]
    topic_counts = Counter(topic_key(item) for item in sessions if topic_key(item) != "general")
    repeated_topics = [(topic, count) for topic, count in topic_counts.most_common(3) if count >= 2]
    context_switches = int(summary.get("context_switches") or 0)
    session_count = len(sessions)

    if low_progress:
        findings.append(
            {
                "title": "Loop risk: high-churn low-progress work",
                "finding": f"{len(low_progress)} scoped session(s) had heavy tool activity without edits, verification, or failures.",
                "recommendation": "Before continuing, name the next concrete deliverable or stop the loop with an explicit parked decision.",
                "severity": "review",
            }
        )
    if repeated_topics:
        topic_text = "; ".join(f"{topic} ({count})" for topic, count in repeated_topics)
        findings.append(
            {
                "title": "Loop risk: repeated topic restarts",
                "finding": f"Repeated topic labels appeared in the scoped window: {topic_text}.",
                "recommendation": "Carry one repeated topic into a single next action, gate, or explicit discard.",
                "severity": "review",
            }
        )
    if edit_without_verify:
        findings.append(
            {
                "title": "Gate: edits without verification",
                "finding": f"{len(edit_without_verify)} edit-bearing scoped session(s) did not record verification-like commands.",
                "recommendation": "Run the narrowest relevant check before treating the work as forward progress.",
                "severity": "review",
            }
        )
    if failures:
        findings.append(
            {
                "title": "Gate: execution failures present",
                "finding": f"{len(failures)} scoped session(s) recorded failed execution commands.",
                "recommendation": "Resolve or explicitly park the failing gate before starting another workflow branch.",
                "severity": "review",
            }
        )
    if session_count >= 4 and context_switches >= max(3, session_count // 2):
        findings.append(
            {
                "title": "Workflow drift: high context switching",
                "finding": f"{context_switches} context switch(es) occurred across {session_count} scoped session(s).",
                "recommendation": "Batch the next run around one repo and one deliverable unless a human explicitly changes focus.",
                "severity": "review",
            }
        )
    return findings


def ensure_thesis(write: bool) -> str:
    if THESIS_PATH.exists():
        return THESIS_PATH.read_text(encoding="utf-8")
    if write:
        THESIS_PATH.parent.mkdir(parents=True, exist_ok=True)
        THESIS_PATH.write_text(DEFAULT_THESIS, encoding="utf-8")
    return DEFAULT_THESIS


def render_synthesis(
    *,
    raw_date: str,
    created_at: str,
    roots: list[tuple[str, Path]],
    thesis_text: str,
    payload: dict[str, Any],
    findings: list[dict[str, Any]],
    log_path: Path,
) -> str:
    summary = payload.get("summary") or {}
    by_scope = Counter(item.get("hermes_scope") or "unknown" for item in payload.get("sessions") or [])
    lines = [
        "---",
        f"date: {raw_date}",
        f"updated_at: {created_at}",
        "status: active",
        "---",
        "",
        f"# Hermes Daily Synthesis - {raw_date}",
        "",
        "## Human Review",
        "",
    ]
    if findings:
        for item in findings:
            lines.extend(
                [
                    f"- **{item['title']}**",
                    f"  - Finding: {item['finding']}",
                    f"  - Suggestion: {item['recommendation']}",
                ]
            )
    else:
        lines.append("- No Hermes findings need human review for this run.")

    lines.extend(
        [
            "",
            "## Review Timing",
            "",
            "- Immediate: this synthesis is updated whenever Hermes runs.",
            "- Background: the heartbeat should summarize review-worthy findings in the thread inbox.",
            "- Morning: `morning-sync` shows a tiny Hermes status line when compatibility findings exist.",
            "- Deep dive: `execution-review` renders full Hermes findings for matching window/runtime reviews.",
            "",
            "## Thesis",
            "",
            first_section(thesis_text),
            "",
            "## Scope",
            "",
            *[f"- {label}: `{path}`" for label, path in roots],
            "",
            "## Workflow Signal",
            "",
            f"- Sessions: {summary.get('sessions', 0)}",
            f"- Wall time: {summary.get('wall_human', '0s')}",
            f"- Context switches: {summary.get('context_switches', 0)}",
            f"- Edits: {summary.get('edits', 0)}",
            f"- Verifications: {summary.get('verifications', 0)}",
            f"- Execution failures: {summary.get('exec_failures', 0)}",
            f"- Scope mix: {', '.join(f'{scope}={count}' for scope, count in sorted(by_scope.items())) or 'none'}",
            "",
            "## Loop Watch",
            "",
            loop_watch(payload),
            "",
            "## Raw Intake",
            "",
            f"- Append log: `{log_path}`",
            "- Raw session identifiers stay in the local log, not this human-facing synthesis.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def first_section(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    body = [line for line in lines if line and not line.startswith("#")]
    return "\n".join(body[:8]) or "Hermes thesis not available."


def loop_watch(payload: dict[str, Any]) -> str:
    sessions = payload.get("sessions") or []
    if not sessions:
        return "- No scoped sessions found in this window."
    topics = Counter(topic_key(item) for item in sessions if topic_key(item) != "general")
    repeated = [f"{topic} ({count})" for topic, count in topics.most_common(5) if count >= 2]
    if repeated:
        return "- Repeated topics: " + "; ".join(repeated)
    return "- No repeated topic labels crossed the simple loop threshold."


def append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")


def existing_compat_ids() -> set[str]:
    if not HERMES_FINDINGS_PATH.exists():
        return set()
    ids: set[str] = set()
    with HERMES_FINDINGS_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if payload.get("id"):
                ids.add(str(payload["id"]))
    return ids


def append_compat_findings(
    *,
    raw_date: str,
    created_at: str,
    window: str,
    runtime: str,
    findings: list[dict[str, Any]],
    synthesis_path: Path,
) -> list[str]:
    if not findings:
        return []
    seen = existing_compat_ids()
    written: list[str] = []
    for item in findings:
        entry_id = f"hermes-daily-{raw_date}-{finding_slug(item['title'])}"
        if entry_id in seen:
            continue
        entry = {
            "id": entry_id,
            "source": "hermes-daily",
            "created_at": created_at,
            "window": window,
            "runtime": runtime,
            "title": item["title"],
            "findings": [item["finding"]],
            "recommendations": [item["recommendation"]],
            "human_review_path": str(synthesis_path),
            "severity": item.get("severity", "review"),
        }
        append_jsonl(HERMES_FINDINGS_PATH, entry)
        written.append(entry_id)
        seen.add(entry_id)
    return written


def stable_run_id(raw_date: str, payload: dict[str, Any], created_at: str) -> str:
    basis = json.dumps(
        {
            "date": raw_date,
            "created_at": created_at,
            "summary": payload.get("summary") or {},
        },
        sort_keys=True,
    )
    return f"hermes-daily-{raw_date}-{hashlib.sha1(basis.encode()).hexdigest()[:10]}"


def main() -> int:
    args = parse_args()
    raw_date = parse_local_date(args.date)
    try:
        window_hours = parse_window(args.window)
    except ValueError:
        sys.stderr.write(f"ERROR: invalid window spec: {args.window}\n")
        return 1

    roots = scope_roots(args.scope_root)
    records = fetch_records(args.runtime, window_hours)
    scoped: list[dict[str, Any]] = []
    for record in records:
        scope = scope_for_cwd(record.get("cwd"), roots)
        if not scope:
            continue
        item = dict(record)
        item["hermes_scope"] = scope
        scoped.append(item)

    payload = aggregate_normalized_sessions(scoped)
    payload["selection"] = {
        "date": raw_date,
        "window": args.window,
        "window_hours": window_hours,
        "runtime": args.runtime,
        "scope_roots": [{"label": label, "path": str(path)} for label, path in roots],
    }
    findings = build_findings(payload, scoped)
    created_at = iso(utc_now()) or ""
    thesis_text = ensure_thesis(args.write)
    log_path = DAILY_DIR / f"{raw_date}-log.jsonl"
    synthesis_path = DAILY_DIR / f"{raw_date}.md"
    log_entry = {
        "id": stable_run_id(raw_date, payload, created_at),
        "source": "hermes-daily",
        "created_at": created_at,
        "date": raw_date,
        "selection": payload["selection"],
        "summary": payload.get("summary") or {},
        "findings": findings,
        "sessions": [session_digest(item) for item in scoped],
    }
    synthesis = render_synthesis(
        raw_date=raw_date,
        created_at=created_at,
        roots=roots,
        thesis_text=thesis_text,
        payload=payload,
        findings=findings,
        log_path=log_path,
    )

    compat_written: list[str] = []
    if args.write:
        upsert_normalized_sessions(scoped)
        append_jsonl(log_path, log_entry)
        synthesis_path.parent.mkdir(parents=True, exist_ok=True)
        synthesis_path.write_text(synthesis, encoding="utf-8")
        if not args.no_compat_findings:
            compat_written = append_compat_findings(
                raw_date=raw_date,
                created_at=created_at,
                window=args.window,
                runtime=args.runtime,
                findings=findings,
                synthesis_path=synthesis_path,
            )

    result = {
        "date": raw_date,
        "write": args.write,
        "sessions": len(scoped),
        "findings": len(findings),
        "human_review_required": bool(findings),
        "thesis_path": str(THESIS_PATH),
        "log_path": str(log_path),
        "synthesis_path": str(synthesis_path),
        "compat_findings_written": compat_written,
    }
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if not args.write:
        sys.stdout.write("\n")
        sys.stdout.write(synthesis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
