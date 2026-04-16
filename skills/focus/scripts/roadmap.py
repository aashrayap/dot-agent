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
    add.add_argument("--section", default="Uncategorized")
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
    rows: list[str] = []
    for item in legacy_items("## Now"):
        rows.append(f"| In Progress | {cell(item)} | - | - | migrated from focus.md |")
    for item in legacy_items("## Next"):
        rows.append(f"| Queued | {cell(item)} | - | - | migrated from focus.md |")
    for item in legacy_items("## Later / Parking Lot"):
        rows.append(f"| Queued | {cell(item)} | - | - | parking lot |")
    for item in legacy_items("## Blockers"):
        rows.append(f"| Blocked | {cell(item)} | - | - | blocker |")

    if not rows:
        rows.append("| Queued | - | - | - | - |")

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
            "## Uncategorized",
            "",
            "| Status | Item | Link | Spec / Idea / Project | Notes |",
            "|--------|------|------|-----------------------|-------|",
            *rows,
        ]
    )


def ensure_roadmap() -> None:
    COLLAB_DIR.mkdir(parents=True, exist_ok=True)
    if ROADMAP_FILE.exists():
        return
    write_text(ROADMAP_FILE, new_roadmap())


def table_header() -> list[str]:
    return [
        "| Status | Item | Link | Spec / Idea / Project | Notes |",
        "|--------|------|------|-----------------------|-------|",
    ]


def section_bounds(lines: list[str], section: str) -> tuple[int, int] | None:
    header = f"## {section}"
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
    if section_bounds(lines, section):
        return lines
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend([f"## {section}", "", *table_header()])
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
    ensure_roadmap()
    lines = ensure_section(update_frontmatter(read_text(ROADMAP_FILE).splitlines(), date_value), section)
    bounds = section_bounds(lines, section)
    if not bounds:
        raise SystemExit(f"ERROR: failed to create section {section!r}")
    _, end = bounds
    row = f"| {normalize_status(status)} | {cell(item)} | {cell(link)} | {cell(source)} | {cell(notes)} |"
    lines = lines[:end] + [row] + lines[end:]
    write_text(ROADMAP_FILE, "\n".join(lines))


def split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def row_matches(line: str, item: str) -> bool:
    parts = split_row(line)
    return len(parts) >= 2 and item.lower() in parts[1].lower()


def mutate_row(item: str, section: str | None, date_value: str, *, status: str | None = None, drop: bool = False) -> None:
    ensure_roadmap()
    lines = update_frontmatter(read_text(ROADMAP_FILE).splitlines(), date_value)
    sections = [section] if section else [line[3:] for line in lines if line.startswith("## ") and line != "## Focus"]
    changed = False
    for section_name in sections:
        bounds = section_bounds(lines, section_name)
        if not bounds:
            continue
        start, end = bounds
        new_body: list[str] = []
        for line in lines[start + 1 : end]:
            if line.startswith("|") and row_matches(line, item):
                if drop:
                    changed = True
                    continue
                if status:
                    parts = split_row(line)
                    if len(parts) >= 5:
                        parts[0] = normalize_status(status)
                        line = "| " + " | ".join(parts[:5]) + " |"
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
    raise SystemExit(f"ERROR: unknown action {args.action!r}")


if __name__ == "__main__":
    raise SystemExit(main())
