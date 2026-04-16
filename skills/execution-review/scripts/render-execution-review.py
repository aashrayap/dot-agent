#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from claude_adapter import fetch_claude_sessions
from codex_adapter import fetch_codex_sessions
from review_context import load_focus_context, load_project_contexts
from review_schema import aggregate_normalized_sessions, iso, parse_window, utc_now
from review_scoring import (
    build_layer_allocation,
    recommendations_from_layer_allocation,
    recommendations_from_scores,
    score_review_payload,
)
from review_store import (
    load_matching_hermes_findings,
    load_recent_history,
    record_review_run,
    report_output_path,
    upsert_normalized_sessions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default="all", choices=["all", "codex", "claude"])
    parser.add_argument("--window", default="day")
    parser.add_argument("--cwd", help="Restrict Codex fetch to one cwd")
    parser.add_argument("--save", action="store_true", help="Write the rendered report to the shared reports dir")
    parser.add_argument("--record", action="store_true", help="Record the review into history.jsonl and review_runs")
    parser.add_argument("--report-slug", help="Slug for the saved markdown report")
    return parser.parse_args()


def _fetch_records(runtime: str, window_hours: float, cwd: str | None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if runtime in {"all", "codex"}:
        records.extend(fetch_codex_sessions(window_hours=window_hours, cwd=cwd))
    if runtime in {"all", "claude"}:
        records.extend(fetch_claude_sessions(window_hours=window_hours))
    return records


def _representative_sessions(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    sessions = payload.get("sessions") or []
    by_wall = sorted(sessions, key=lambda item: int(item.get("wall_seconds") or 0), reverse=True)
    risky_verify = [s for s in sessions if int(s.get("edits") or 0) > 0 and int(s.get("verifications") or 0) == 0]
    risky_fit = [s for s in sessions if sum(int(v or 0) for v in ((s.get("response_fit") or {}).get("feedback_signals") or {}).values()) > 0]
    failing = [s for s in sessions if int(s.get("exec_failures") or 0) > 0]
    return {
        "top_by_wall": by_wall[:3],
        "verification_risks": risky_verify[:3],
        "response_fit_risks": risky_fit[:3],
        "failing_sessions": failing[:3],
    }


def _recurring_patterns(payload: dict[str, Any], recent_history: list[dict[str, Any]]) -> list[str]:
    patterns: list[str] = []
    sessions = payload.get("sessions") or []
    edit_without_verify = sum(
        1 for s in sessions if int(s.get("edits") or 0) > 0 and int(s.get("verifications") or 0) == 0
    )
    if edit_without_verify:
        patterns.append(f"{edit_without_verify} session(s) edited without verification.")

    fit_feedback_sessions = sum(
        1
        for s in sessions
        if sum(int(v or 0) for v in ((s.get("response_fit") or {}).get("feedback_signals") or {}).values()) > 0
    )
    if fit_feedback_sessions:
        patterns.append(f"{fit_feedback_sessions} session(s) showed response-fit correction signals.")

    if recent_history:
        same_window = [entry for entry in recent_history if entry.get("window") == payload.get("selection", {}).get("window")]
        if same_window:
            patterns.append(f"{len(same_window)} prior review entry/entries exist for the same window class.")
    return patterns


def _topline(payload: dict[str, Any], scores: dict[str, dict[str, Any]]) -> list[str]:
    summary = payload.get("summary") or {}
    by_runtime = payload.get("by_runtime") or []
    runtime_bits = ", ".join(f"{row['runtime']}={row['sessions']}" for row in by_runtime) or "no sessions"
    lines = [
        f"{summary.get('sessions', 0)} session(s) across {summary.get('unique_cwds', 0)} cwd(s); runtime mix: {runtime_bits}.",
        f"Context switches: {summary.get('context_switches', 0)}. Edits: {summary.get('edits', 0)}. Verifications: {summary.get('verifications', 0)}. Failures: {summary.get('exec_failures', 0)}.",
        (
            f"Lowest scores: "
            + ", ".join(
                f"{name.replace('_', ' ')}={meta['score']}"
                for name, meta in sorted(scores.items(), key=lambda item: item[1]["score"])[:2]
            )
            + "."
        ),
    ]
    return lines


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _render_report(
    *,
    created_at: str,
    payload: dict[str, Any],
    scores: dict[str, dict[str, Any]],
    recommendations: list[str],
    recurring_patterns: list[str],
    hermes_findings: list[dict[str, Any]],
    focus_context: dict[str, Any],
    project_contexts: list[dict[str, Any]],
    layer_allocation: dict[str, Any],
) -> str:
    lines: list[str] = []
    selection = payload.get("selection") or {}
    summary = payload.get("summary") or {}
    representatives = _representative_sessions(payload)
    created_label = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")

    lines.append(f"# Execution Review — {created_label}")
    lines.append("")
    lines.append("## Topline")
    for line in _topline(payload, scores):
        lines.append(f"- {line}")
    lines.append("")

    runtime_rows = [
        [
            row["runtime"],
            str(row["sessions"]),
            row["wall_human"],
            str(row["edits"]),
            str(row["verifications"]),
            str(row["exec_failures"]),
        ]
        for row in payload.get("by_runtime") or []
    ]
    if runtime_rows:
        lines.append("## Runtime Breakdown")
        lines.append(_markdown_table(["Runtime", "Sessions", "Wall", "Edits", "Verify", "Failures"], runtime_rows))
        lines.append("")

    layer_rows = []
    for layer in ["strategic", "tactical", "disposable"]:
        bucket = layer_allocation.get(layer) or {}
        layer_rows.append(
            [
                layer.title(),
                str(bucket.get("sessions", 0)),
                f"{int(float(bucket.get('wall_ratio') or 0) * 100)}%",
                (bucket.get("examples") or [{}])[0].get("reason", ""),
            ]
        )
    lines.append("## Strategic / Tactical / Disposable Lens")
    lines.append(_markdown_table(["Layer", "Sessions", "Wall Share", "Read"], layer_rows))
    lines.append("")

    score_rows = [
        [name.replace("_", " ").title(), str(meta["score"]), meta["why"]]
        for name, meta in scores.items()
    ]
    lines.append("## Scorecard")
    lines.append(_markdown_table(["Dimension", "Score", "Why"], score_rows))
    lines.append("")

    if recurring_patterns:
        lines.append("## Recurring Patterns")
        for item in recurring_patterns:
            lines.append(f"- {item}")
        lines.append("")

    if focus_context.get("exists"):
        lines.append("## Focus Context")
        if focus_context.get("focus"):
            lines.append(f"- Focus: {focus_context['focus']}")
        if focus_context.get("in_progress"):
            lines.append(f"- In Progress: {', '.join(focus_context['in_progress'])}")
        if focus_context.get("queued"):
            lines.append(f"- Queued: {', '.join(focus_context['queued'])}")
        if focus_context.get("done"):
            lines.append(f"- Done: {', '.join(focus_context['done'])}")
        lines.append("")

    if project_contexts:
        lines.append("## Project Execution Context")
        for project in project_contexts:
            lines.append(f"- **{project['slug']}** (`{project['status']}`)")
            if project.get("goal"):
                lines.append(f"  - Goal: {project['goal']}")
            if project.get("progress_summary"):
                lines.append(f"  - Progress: {project['progress_summary']}")
            if project.get("open_followups"):
                lines.append(f"  - Follow-ups: {project['open_followups']}")
            if project.get("blockers"):
                lines.append(f"  - Blockers: {project['blockers']}")
        lines.append("")

    rep_sections = [
        ("Top Sessions By Wall Time", representatives["top_by_wall"]),
        ("Verification Risks", representatives["verification_risks"]),
        ("Response Fit Risks", representatives["response_fit_risks"]),
        ("Failing Sessions", representatives["failing_sessions"]),
    ]
    for title, items in rep_sections:
        if not items:
            continue
        lines.append(f"## {title}")
        for session in items:
            lines.append(
                f"- `{session['runtime']}` `{session['session_id']}` — {session.get('label','')} | "
                f"wall `{session.get('wall_human')}` | cwd `{session.get('cwd')}`"
            )
        lines.append("")

    if hermes_findings:
        lines.append("## Hermes Findings")
        for finding in hermes_findings:
            title = finding.get("title") or finding.get("id") or "Hermes finding"
            lines.append(f"- **{title}**")
            for text in finding.get("findings") or []:
                lines.append(f"  - {text}")
            for text in finding.get("recommendations") or []:
                lines.append(f"  - Recommendation: {text}")
        lines.append("")

    lines.append("## Recommended Changes")
    if recommendations:
        for idx, rec in enumerate(recommendations, start=1):
            lines.append(f"{idx}. {rec}")
    else:
        lines.append("1. Keep the current workflow, but continue collecting evidence before changing defaults.")
    lines.append("")

    lines.append("## Review Context")
    lines.append(f"- Window: `{selection.get('window')}`")
    lines.append(f"- Runtime: `{selection.get('runtime')}`")
    lines.append(f"- Sessions: `{summary.get('sessions', 0)}`")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    window_hours = parse_window(args.window)
    records = _fetch_records(args.runtime, window_hours, args.cwd)
    upsert_normalized_sessions(records)
    payload = aggregate_normalized_sessions(records)
    payload["selection"] = {
        "runtime": args.runtime,
        "window": args.window,
        "window_hours": window_hours,
        "cwd": args.cwd,
    }
    hermes_findings = load_matching_hermes_findings(args.window, args.runtime)
    payload["hermes_findings"] = hermes_findings
    focus_context = load_focus_context()
    project_contexts = load_project_contexts(payload.get("sessions") or [], focus_context)
    payload["focus_context"] = focus_context
    payload["project_contexts"] = project_contexts

    scores = score_review_payload(payload)
    layer_allocation = build_layer_allocation(payload)
    recommendations = recommendations_from_layer_allocation(layer_allocation) + recommendations_from_scores(scores)
    recommendations = recommendations[:3]
    recent_history = load_recent_history(10)
    recurring_patterns = _recurring_patterns(payload, recent_history)

    created_at = iso(utc_now()) or ""
    report = _render_report(
        created_at=created_at,
        payload=payload,
        scores=scores,
        recommendations=recommendations,
        recurring_patterns=recurring_patterns,
        hermes_findings=hermes_findings,
        focus_context=focus_context,
        project_contexts=project_contexts,
        layer_allocation=layer_allocation,
    )

    report_path = None
    if args.save:
        slug = args.report_slug or f"execution-review-{created_at[:10]}-{args.runtime}-{args.window}-{uuid4().hex[:8]}"
        report_path = report_output_path(slug)
        report_path.write_text(report, encoding="utf-8")

    if args.record:
        review_id = args.report_slug or f"review-{uuid4().hex[:12]}"
        history_entry = {
            "review_id": review_id,
            "created_at": created_at,
            "window": args.window,
            "runtime": args.runtime,
            "summary": payload["summary"],
            "by_runtime": payload.get("by_runtime") or [],
            "scores": {name: meta["score"] for name, meta in scores.items()},
            "score_reasons": {name: meta["why"] for name, meta in scores.items()},
            "layer_allocation": layer_allocation,
            "observations": recurring_patterns,
            "proposed_changes": recommendations,
            "hermes_findings": [finding.get("id") or finding.get("title") for finding in hermes_findings],
            "focus_context": focus_context.get("focus", ""),
            "project_contexts": [project["slug"] for project in project_contexts],
            "report_path": str(report_path) if report_path else None,
        }
        record_review_run(
            review_id=review_id,
            window=args.window,
            runtime=args.runtime,
            created_at=created_at,
            report_path=str(report_path) if report_path else None,
            history_entry=history_entry,
        )

    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
