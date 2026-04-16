#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory under ~/.dot-agent/state/projects/<slug>")
    subparsers = parser.add_subparsers(dest="action", required=True)

    session = subparsers.add_parser("session", help="Append a PR row and refresh summary/metrics for a completed session")
    session.add_argument("--date", required=True)
    session.add_argument("--session", required=True)
    session.add_argument("--outcome", required=True)
    session.add_argument("--ref", default="")
    session.add_argument("--notes", default="")

    ref = subparsers.add_parser("ref", help="Append a PR/ref row")
    ref.add_argument("--pr", required=True)
    ref.add_argument("--status", required=True)
    ref.add_argument("--scope", required=True)
    ref.add_argument("--notes", default="")
    ref.add_argument("--date", default="")

    pivot = subparsers.add_parser("pivot", help="Append a pivot/change row")
    pivot.add_argument("--date", required=True)
    pivot.add_argument("--change", required=True)
    pivot.add_argument("--why", required=True)

    summary = subparsers.add_parser("summary", help="Rewrite progress summary")
    summary.add_argument("--text", required=True)
    summary.add_argument("--date", required=True)

    followup = subparsers.add_parser("followup", help="Append an open follow-up item")
    followup.add_argument("--text", required=True)
    followup.add_argument("--date", required=True)

    subparsers.add_parser("recalc", help="Recompute effort summary")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}")


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to write {path}: {exc}")


def section_bounds(lines: list[str], header: str) -> tuple[int, int]:
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise SystemExit(f"ERROR: missing section {header!r}") from exc
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != header:
            end = idx
            break
    return start, end


def replace_section_body(lines: list[str], header: str, body_lines: list[str]) -> list[str]:
    start, end = section_bounds(lines, header)
    replacement = [header, ""] + body_lines
    return lines[:start] + replacement + lines[end:]


def update_last_touched(lines: list[str], date_value: str) -> list[str]:
    if not date_value:
        return lines
    out: list[str] = []
    for line in lines:
        if line.startswith("last_touched:"):
            out.append(f"last_touched: {date_value}")
        else:
            out.append(line)
    return out


def insert_table_row(lines: list[str], header: str, row: str) -> list[str]:
    _, end = section_bounds(lines, header)
    return lines[:end] + [row] + lines[end:]


def table_row_count(lines: list[str], header: str) -> int:
    start, end = section_bounds(lines, header)
    count = 0
    for line in lines[start + 3 : end]:
        stripped = line.strip()
        if stripped.startswith("|") and not set(stripped.replace("|", "").strip()) <= {"-", " "}:
            count += 1
    return count


def table_status_count(lines: list[str], header: str, status_value: str) -> int:
    start, end = section_bounds(lines, header)
    count = 0
    expected = status_value.lower()
    for line in lines[start + 3 : end]:
        stripped = line.strip()
        if not stripped.startswith("|") or set(stripped.replace("|", "").strip()) <= {"-", " "}:
            continue
        parts = [part.strip().lower() for part in stripped.strip("|").split("|")]
        if len(parts) >= 2 and expected in parts[1]:
            count += 1
    return count


def current_metric(lines: list[str], metric_name: str) -> int:
    start, end = section_bounds(lines, "## Effort Summary")
    needle = f"| {metric_name} |"
    for line in lines[start + 3 : end]:
        if line.startswith(needle):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    return 0
    return 0


def recalc_effort_summary(lines: list[str], *, session_count: int | None = None) -> list[str]:
    pr_count = table_row_count(lines, "## PRs")
    discarded_count = table_status_count(lines, "## PRs", "discarded")
    pivot_count = table_row_count(lines, "## Pivots & Changes")
    start, end = section_bounds(lines, "## Open Follow-ups")
    followup_count = len([line for line in lines[start + 2 : end] if line.strip().startswith("-")])
    if session_count is None:
        session_count = current_metric(lines, "Sessions completed")
    replacement = [
        "## Effort Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Sessions completed | {session_count} |",
        f"| PRs logged | {pr_count} |",
        f"| Discarded PRs | {discarded_count} |",
        f"| Pivots logged | {pivot_count} |",
        f"| Open follow-ups | {followup_count} |",
        "| Compression | — |",
        "| Precision | — |",
    ]
    start, end = section_bounds(lines, "## Effort Summary")
    return lines[:start] + replacement + lines[end:]


def _section(lines: list[str], header: str) -> list[str]:
    start, end = section_bounds(lines, header)
    return [line for line in lines[start + 1 : end] if line.strip()]


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser()
    execution_file = project_dir / "execution.md"
    if not execution_file.exists():
        raise SystemExit(f"ERROR: execution.md not found: {execution_file}")

    lines = read_text(execution_file).splitlines()

    session_count = None

    if args.action == "session":
        lines = update_last_touched(lines, args.date)
        summary = f"{args.date}: {args.outcome}"
        if args.notes:
            summary += f" ({args.notes})"
        lines = replace_section_body(lines, "## Progress Summary", [summary])
        session_count = current_metric(lines, "Sessions completed") + 1
        if args.ref:
            lines = insert_table_row(
                lines,
                "## PRs",
                f"| {args.ref} | logged | {args.outcome} | {args.notes} |",
            )
    elif args.action == "ref":
        lines = update_last_touched(lines, args.date)
        lines = insert_table_row(
            lines,
            "## PRs",
            f"| {args.pr} | {args.status} | {args.scope} | {args.notes} |",
        )
    elif args.action == "pivot":
        lines = update_last_touched(lines, args.date)
        lines = insert_table_row(
            lines,
            "## Pivots & Changes",
            f"| {args.date} | {args.change} | {args.why} |",
        )
    elif args.action == "summary":
        lines = update_last_touched(lines, args.date)
        lines = replace_section_body(lines, "## Progress Summary", [args.text])
    elif args.action == "followup":
        lines = update_last_touched(lines, args.date)
        start, end = section_bounds(lines, "## Open Follow-ups")
        body = [line for line in lines[start + 2 : end] if line.strip()]
        body.append(f"- {args.text}")
        lines = replace_section_body(lines, "## Open Follow-ups", body)
    elif args.action == "recalc":
        pass
    else:
        raise SystemExit(f"ERROR: unknown action: {args.action}")

    lines = recalc_effort_summary(lines, session_count=session_count)
    write_text(execution_file, "\n".join(lines).rstrip() + "\n")
    print(f"UPDATED={execution_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
