#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
DOT_AGENT_STATE_HOME = Path(os.environ.get("DOT_AGENT_STATE_HOME", str(DOT_AGENT_HOME / "state"))).expanduser()
COLLAB_DIR = DOT_AGENT_STATE_HOME / "collab"
ROADMAP_FILE = COLLAB_DIR / "roadmap.md"
FOCUS_FILE = COLLAB_DIR / "focus.md"

STATUSES = {
    "queued": "Queued",
    "in-progress": "In Progress",
    "in progress": "In Progress",
    "completed": "Completed",
    "complete": "Completed",
    "blocked": "Blocked",
    "review": "Review",
    "needs-review": "Needs Review",
    "needs review": "Needs Review",
    "waiting": "Waiting",
    "follow-up": "Follow-up",
    "follow up": "Follow-up",
    "dropped": "Dropped",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("setup", help="Ensure roadmap.md exists")
    sub.add_parser("show", help="Print roadmap.md")

    focus = sub.add_parser("focus", help="Set the focus prose")
    focus.add_argument("--date", default=date.today().isoformat())
    focus.add_argument("--text", required=True)

    add = sub.add_parser("add", help="Add a row")
    add.add_argument("--date", default=date.today().isoformat())
    add.add_argument("--section", default="Active Projects")
    add.add_argument("--status", default="Queued")
    add.add_argument("--item", required=True)
    add.add_argument("--link", default="-")
    add.add_argument("--source", default="-")
    add.add_argument("--notes", default="-")

    status = sub.add_parser("status", help="Change row status by item substring")
    status.add_argument("--date", default=date.today().isoformat())
    status.add_argument("--item", required=True)
    status.add_argument("--status", required=True)
    status.add_argument("--section")

    drop = sub.add_parser("drop", help="Remove a row by item substring")
    drop.add_argument("--date", default=date.today().isoformat())
    drop.add_argument("--item", required=True)
    drop.add_argument("--section")
    drop.add_argument("--why", default="")

    review = sub.add_parser("review", help="Write a daily recap and optionally drain completed rows")
    review.add_argument("--date", default=date.today().isoformat())
    review.add_argument("--tomorrow", default="Review the remaining roadmap rows and continue the highest-leverage unblocked work.")
    review.add_argument("--note", action="append", default=[], help="Extra note to append to the recap")
    review.add_argument("--dry-run", action="store_true", help="Print the recap without writing or draining")
    review.add_argument("--write", action="store_true", help="Write the dated recap and drain completed rows")
    review.add_argument("--no-drain", action="store_true", help="Write the recap without draining completed rows")
    review.add_argument("--force", action="store_true", help="Overwrite an existing dated recap")

    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to write {path}: {exc}") from exc


def normalize_status(value: str) -> str:
    normalized = " ".join(value.strip().lower().replace("_", "-").split())
    if normalized not in STATUSES:
        raise SystemExit(f"ERROR: invalid status {value!r}; expected one of {sorted(set(STATUSES.values()))}")
    return STATUSES[normalized]


def cell(value: str) -> str:
    cleaned = " ".join((value or "-").split())
    cleaned = cleaned.replace("|", "/")
    return cleaned or "-"


def focus_section_from_legacy() -> str:
    text = read_text(FOCUS_FILE)
    if not text:
        return "None set yet."
    lines = text.splitlines()
    try:
        start = lines.index("## Current Focus")
    except ValueError:
        return "None set yet."
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        value = line.strip()
        if value:
            return value
    return "None set yet."


def legacy_items(header: str) -> list[str]:
    text = read_text(FOCUS_FILE)
    if not text:
        return []
    lines = text.splitlines()
    try:
        start = lines.index(header)
    except ValueError:
        return []
    out: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        value = line.strip()
        if value.startswith("- "):
            item = value[2:].strip()
            if item and item.lower() != "none":
                out.append(item)
    return out


def new_roadmap() -> str:
    today = date.today().isoformat()
    focus = focus_section_from_legacy()
    active_rows: list[str] = []
    parked_rows: list[str] = []
    for item in legacy_items("## Now"):
        active_rows.append(f"| General | In Progress | {cell(item)} | - | migrated from focus.md |")
    for item in legacy_items("## Next"):
        active_rows.append(f"| General | Queued | {cell(item)} | - | migrated from focus.md |")
    for item in legacy_items("## Later / Parking Lot"):
        parked_rows.append(f"| {cell(item)} | parking lot | - |")
    for item in legacy_items("## Blockers"):
        parked_rows.append(f"| {cell(item)} | blocker | - |")

    if not active_rows:
        active_rows.append("| General | Queued | - | - | - |")

    return "\n".join(
        [
            "---",
            f"last_sync: {today}",
            f"last_touched: {today}",
            "---",
            "",
            "# Roadmap",
            "",
            "## Focus",
            "",
            focus,
            "",
            "## Active Projects",
            "",
            "| Project | Status | Task | Link | Notes |",
            "|---------|--------|------|------|-------|",
            *active_rows,
            "",
            "## Review Queue",
            "",
            "| Item | Source | Status | Notes |",
            "|------|--------|--------|-------|",
            "",
            "## Parked / Blocked",
            "",
            "| Item | Reason | Revisit |",
            "|------|--------|---------|",
            *parked_rows,
        ]
    )


def ensure_roadmap() -> None:
    COLLAB_DIR.mkdir(parents=True, exist_ok=True)
    if ROADMAP_FILE.exists():
        return
    write_text(ROADMAP_FILE, new_roadmap())


def normalized_section(section: str) -> str:
    value = " ".join(section.strip().lower().split())
    aliases = {
        "active": "Active Projects",
        "active projects": "Active Projects",
        "review": "Review Queue",
        "review queue": "Review Queue",
        "parked": "Parked / Blocked",
        "blocked": "Parked / Blocked",
        "parked / blocked": "Parked / Blocked",
        "parked/blocked": "Parked / Blocked",
    }
    return aliases.get(value, section.strip() or "Active Projects")


def table_header(section: str) -> list[str]:
    section = normalized_section(section)
    if section == "Active Projects":
        return [
            "| Project | Status | Task | Link | Notes |",
            "|---------|--------|------|------|-------|",
        ]
    if section == "Review Queue":
        return [
            "| Item | Source | Status | Notes |",
            "|------|--------|--------|-------|",
        ]
    if section == "Parked / Blocked":
        return [
            "| Item | Reason | Revisit |",
            "|------|--------|---------|",
        ]
    return [
        "| Project | Status | Task | Link | Notes |",
        "|---------|--------|------|------|-------|",
    ]


def section_bounds(lines: list[str], section: str) -> tuple[int, int] | None:
    header = f"## {normalized_section(section)}"
    try:
        start = lines.index(header)
    except ValueError:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return start, end


def ensure_section(lines: list[str], section: str) -> list[str]:
    section = normalized_section(section)
    if section_bounds(lines, section):
        return lines
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend([f"## {section}", "", *table_header(section)])
    return lines


def update_frontmatter(lines: list[str], date_value: str) -> list[str]:
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.startswith("last_touched:"):
            out.append(f"last_touched: {date_value}")
            replaced = True
        else:
            out.append(line)
    if not replaced and out and out[0] == "---":
        out.insert(2, f"last_touched: {date_value}")
    return out


def set_focus(text: str, date_value: str) -> None:
    ensure_roadmap()
    lines = update_frontmatter(read_text(ROADMAP_FILE).splitlines(), date_value)
    bounds = section_bounds(lines, "Focus")
    if not bounds:
        insert = 4 if len(lines) >= 4 else len(lines)
        lines[insert:insert] = ["", "## Focus", "", text]
    else:
        start, end = bounds
        lines = lines[: start + 1] + ["", text, ""] + lines[end:]
    write_text(ROADMAP_FILE, "\n".join(lines))


def add_row(section: str, status: str, item: str, link: str, source: str, notes: str, date_value: str) -> None:
    section = normalized_section(section)
    ensure_roadmap()
    lines = ensure_section(update_frontmatter(read_text(ROADMAP_FILE).splitlines(), date_value), section)
    bounds = section_bounds(lines, section)
    if not bounds:
        raise SystemExit(f"ERROR: failed to create section {section!r}")
    start, end = bounds
    if section == "Active Projects":
        project = cell(source if source != "-" else "General")
        row = f"| {project} | {normalize_status(status)} | {cell(item)} | {cell(link)} | {cell(notes)} |"
    elif section == "Review Queue":
        row = f"| {cell(item)} | {cell(source)} | {normalize_status(status)} | {cell(notes)} |"
    elif section == "Parked / Blocked":
        reason = cell(notes if notes != "-" else source)
        revisit = cell(link)
        row = f"| {cell(item)} | {reason} | {revisit} |"
    else:
        row = f"| {cell(source if source != '-' else 'General')} | {normalize_status(status)} | {cell(item)} | {cell(link)} | {cell(notes)} |"
    insert_at = end
    while insert_at > start and not lines[insert_at - 1].strip():
        insert_at -= 1
    body = lines[start + 1 : insert_at]
    if any(line.strip() in {"| General | Queued | - | - | - |", "| - | - | - |"} for line in body):
        body = [line for line in body if line.strip() not in {"| General | Queued | - | - | - |", "| - | - | - |"}]
        lines = lines[: start + 1] + body + lines[insert_at:]
        insert_at = start + 1 + len(body)
    lines = lines[:insert_at] + [row] + lines[insert_at:]
    write_text(ROADMAP_FILE, "\n".join(lines))


def split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def is_table_divider(parts: list[str]) -> bool:
    return bool(parts) and all(set(part.replace(":", "").strip()) <= {"-"} for part in parts)


def roadmap_rows(section: str) -> list[list[str]]:
    ensure_roadmap()
    lines = read_text(ROADMAP_FILE).splitlines()
    bounds = section_bounds(lines, section)
    if not bounds:
        return []
    start, end = bounds
    rows: list[list[str]] = []
    for line in lines[start + 1 : end]:
        if not line.startswith("|"):
            continue
        parts = split_row(line)
        if not parts or is_table_divider(parts):
            continue
        if parts[0] in {"Project", "Item"}:
            continue
        if all(part in {"", "-"} for part in parts):
            continue
        rows.append(parts)
    return rows


def active_row_bullet(row: list[str], *, include_status: bool) -> str:
    project = row[0] if len(row) > 0 else "General"
    status = row[1] if len(row) > 1 else "-"
    task = row[2] if len(row) > 2 else "-"
    link = row[3] if len(row) > 3 else "-"
    notes = row[4] if len(row) > 4 else "-"
    suffix: list[str] = []
    if link != "-":
        suffix.append(link)
    if notes != "-":
        suffix.append(notes)
    status_prefix = f"[{status}] " if include_status else ""
    detail = f" ({'; '.join(suffix)})" if suffix else ""
    return f"- {project}: {status_prefix}{task}{detail}"


def review_row_bullet(row: list[str]) -> str:
    item = row[0] if len(row) > 0 else "-"
    source = row[1] if len(row) > 1 else "-"
    status = row[2] if len(row) > 2 else "-"
    notes = row[3] if len(row) > 3 else "-"
    suffix = ", ".join(part for part in [source, status, notes] if part and part != "-")
    return f"- {item}" + (f" ({suffix})" if suffix else "")


def parked_row_bullet(row: list[str]) -> str:
    item = row[0] if len(row) > 0 else "-"
    reason = row[1] if len(row) > 1 else "-"
    revisit = row[2] if len(row) > 2 else "-"
    suffix = ", ".join(part for part in [reason, revisit] if part and part != "-")
    return f"- {item}" + (f" ({suffix})" if suffix else "")


def build_daily_review(date_value: str, tomorrow: str, notes: list[str]) -> tuple[str, list[str]]:
    active_rows = roadmap_rows("Active Projects")
    review_rows = roadmap_rows("Review Queue")
    parked_rows = roadmap_rows("Parked / Blocked")

    completed = [
        row for row in active_rows if len(row) > 2 and row[1].strip().lower() == "completed" and row[2] != "-"
    ]
    still_open = [
        row
        for row in active_rows
        if len(row) > 2 and row[2] != "-" and row[1].strip().lower() != "completed"
    ]

    completed_lines = [active_row_bullet(row, include_status=False) for row in completed] or ["- No completed rows recorded"]
    open_lines = [active_row_bullet(row, include_status=True) for row in still_open] or ["- No open roadmap rows"]
    review_lines = [review_row_bullet(row) for row in review_rows] or ["- No tracked queue"]
    parked_lines = [parked_row_bullet(row) for row in parked_rows] or ["- No parked or blocked rows"]
    note_lines = [f"- {cell(note)}" for note in notes if note.strip()]

    lines = [
        f"# Daily Review - {date_value}",
        "",
        "## Completed",
        *completed_lines,
        "",
        "## Still Open",
        *open_lines,
        "",
        "## Review Queue",
        *review_lines,
        "",
        "## Parked / Blocked",
        *parked_lines,
        "",
        "## Tomorrow Handoff",
        f"- {cell(tomorrow)}",
    ]
    if note_lines:
        lines.extend(["", "## Notes", *note_lines])
    return "\n".join(lines).rstrip() + "\n", [row[2] for row in completed]


def touch_roadmap(date_value: str) -> None:
    ensure_roadmap()
    original = read_text(ROADMAP_FILE).splitlines()
    lines = update_frontmatter(original, date_value)
    if lines != original:
        write_text(ROADMAP_FILE, "\n".join(lines))


def drain_completed_rows(date_value: str) -> int:
    ensure_roadmap()
    original = read_text(ROADMAP_FILE).splitlines()
    lines = update_frontmatter(original, date_value)
    bounds = section_bounds(lines, "Active Projects")
    if not bounds:
        if lines != original:
            write_text(ROADMAP_FILE, "\n".join(lines))
        return 0
    start, end = bounds
    new_body: list[str] = []
    drained = 0
    for line in lines[start + 1 : end]:
        if line.startswith("|"):
            parts = split_row(line)
            if (
                len(parts) > 2
                and not is_table_divider(parts)
                and parts[0] != "Project"
                and parts[1].strip().lower() == "completed"
                and parts[2] != "-"
            ):
                drained += 1
                continue
        new_body.append(line)
    if drained or lines != original:
        lines = lines[: start + 1] + new_body + lines[end:]
        write_text(ROADMAP_FILE, "\n".join(lines))
    return drained


def write_daily_review(date_value: str, tomorrow: str, notes: list[str], *, drain: bool, force: bool) -> tuple[Path, int, int]:
    recap, completed_items = build_daily_review(date_value, tomorrow, notes)
    recap_dir = COLLAB_DIR / "daily-reviews"
    recap_path = recap_dir / f"{date_value}.md"
    if recap_path.exists() and not force:
        raise SystemExit(f"ERROR: {recap_path} already exists; pass --force to overwrite it")
    recap_dir.mkdir(parents=True, exist_ok=True)
    recap_path.write_text(recap, encoding="utf-8")
    drained = drain_completed_rows(date_value) if drain else 0
    if not drain:
        touch_roadmap(date_value)
    return recap_path, len(completed_items), drained


def item_column(section: str) -> int:
    section = normalized_section(section)
    if section == "Active Projects":
        return 2
    return 0


def status_column(section: str) -> int | None:
    section = normalized_section(section)
    if section == "Active Projects":
        return 1
    if section == "Review Queue":
        return 2
    return None


def row_matches(line: str, item: str, section: str) -> bool:
    parts = split_row(line)
    idx = item_column(section)
    return len(parts) > idx and item.lower() in parts[idx].lower()


def mutate_row(item: str, section: str | None, date_value: str, *, status: str | None = None, drop: bool = False) -> None:
    ensure_roadmap()
    lines = update_frontmatter(read_text(ROADMAP_FILE).splitlines(), date_value)
    sections = [normalized_section(section)] if section else [line[3:] for line in lines if line.startswith("## ") and line != "## Focus"]
    changed = False
    for section_name in sections:
        bounds = section_bounds(lines, section_name)
        if not bounds:
            continue
        start, end = bounds
        new_body: list[str] = []
        for line in lines[start + 1 : end]:
            if line.startswith("|") and row_matches(line, item, section_name):
                if drop:
                    changed = True
                    continue
                if status:
                    parts = split_row(line)
                    idx = status_column(section_name)
                    if idx is None:
                        raise SystemExit(f"ERROR: section {section_name!r} has no status column")
                    if len(parts) > idx:
                        parts[idx] = normalize_status(status)
                        line = "| " + " | ".join(parts) + " |"
                        changed = True
            new_body.append(line)
        lines = lines[: start + 1] + new_body + lines[end:]
    if not changed:
        raise SystemExit(f"ERROR: no roadmap row matched {item!r}")
    write_text(ROADMAP_FILE, "\n".join(lines))


def main() -> int:
    args = parse_args()
    if args.action == "setup":
        ensure_roadmap()
        print(f"ROADMAP_FILE={ROADMAP_FILE}")
        print(f"FOCUS_FILE={FOCUS_FILE}")
        return 0
    if args.action == "show":
        ensure_roadmap()
        print(read_text(ROADMAP_FILE), end="")
        return 0
    if args.action == "focus":
        set_focus(args.text, args.date)
        print(f"UPDATED={ROADMAP_FILE}")
        return 0
    if args.action == "add":
        add_row(args.section, args.status, args.item, args.link, args.source, args.notes, args.date)
        print(f"UPDATED={ROADMAP_FILE}")
        return 0
    if args.action == "status":
        mutate_row(args.item, args.section, args.date, status=args.status)
        print(f"UPDATED={ROADMAP_FILE}")
        return 0
    if args.action == "drop":
        mutate_row(args.item, args.section, args.date, drop=True)
        print(f"UPDATED={ROADMAP_FILE}")
        return 0
    if args.action == "review":
        if args.dry_run:
            args.write = False
        drain = bool(args.write and not args.no_drain)
        if args.write:
            recap_path, completed_count, drained_count = write_daily_review(
                args.date,
                args.tomorrow,
                args.note,
                drain=drain,
                force=args.force,
            )
            print(f"RECAP_FILE={recap_path}")
            print(f"COMPLETED_COUNT={completed_count}")
            print(f"DRAINED_COUNT={drained_count}")
            print(f"ROADMAP_FILE={ROADMAP_FILE}")
            return 0
        recap, completed_items = build_daily_review(args.date, args.tomorrow, args.note)
        print(recap, end="")
        print(f"\nCOMPLETED_COUNT={len(completed_items)}")
        print("DRAINED_COUNT=0")
        print(f"ROADMAP_FILE={ROADMAP_FILE}")
        return 0
    raise SystemExit(f"ERROR: unknown action {args.action!r}")


if __name__ == "__main__":
    raise SystemExit(main())
