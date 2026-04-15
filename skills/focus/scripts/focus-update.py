#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
DOT_AGENT_STATE_HOME = Path(
    os.environ.get("DOT_AGENT_STATE_HOME", str(DOT_AGENT_HOME / "state"))
).expanduser()
FOCUS_FILE = DOT_AGENT_STATE_HOME / "collab" / "focus.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)

    show = subparsers.add_parser("show", help="Print the current focus file")
    show.add_argument("--path-only", action="store_true")

    set_parser = subparsers.add_parser("set", help="Rewrite focus state")
    set_parser.add_argument("--date", required=True)
    set_parser.add_argument("--current", required=True)
    set_parser.add_argument("--why", required=True)
    set_parser.add_argument("--now", action="append")
    set_parser.add_argument("--next", dest="next_items", action="append")
    set_parser.add_argument("--later", action="append")
    set_parser.add_argument("--blocker", action="append")

    park = subparsers.add_parser("park", help="Move an item to later/parking lot")
    park.add_argument("--date", required=True)
    park.add_argument("--item", required=True)
    park.add_argument("--why", required=True)

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
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.startswith("last_touched:"):
            out.append(f"last_touched: {date_value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.insert(2, f"last_touched: {date_value}")
    return out


def current_focus(lines: list[str]) -> str:
    start, end = section_bounds(lines, "## Current Focus")
    for line in lines[start + 1 : end]:
        value = line.strip()
        if value:
            return value
    return "None set yet."


def normalize_list(items: list[str]) -> list[str]:
    cleaned = [item.strip() for item in items if item.strip()]
    return cleaned or ["None"]


def maybe_replace_list_section(lines: list[str], header: str, items: list[str] | None) -> list[str]:
    if items is None:
        return lines
    return replace_section_body(lines, header, [f"- {item}" for item in normalize_list(items)])


def main() -> int:
    args = parse_args()
    if args.action == "show":
        if args.path_only:
            print(FOCUS_FILE)
        else:
            print(read_text(FOCUS_FILE), end="")
        return 0

    lines = read_text(FOCUS_FILE).splitlines()

    if args.action == "set":
        old_focus = current_focus(lines)
        lines = update_last_touched(lines, args.date)
        lines = replace_section_body(lines, "## Current Focus", [args.current])
        lines = maybe_replace_list_section(lines, "## Now", args.now)
        lines = maybe_replace_list_section(lines, "## Next", args.next_items)
        lines = maybe_replace_list_section(lines, "## Later / Parking Lot", args.later)
        lines = maybe_replace_list_section(lines, "## Blockers", args.blocker)
        if old_focus != args.current:
            start, end = section_bounds(lines, "## Recent Shifts")
            row = f"| {args.date} | {old_focus} | {args.current} | {args.why} |"
            insert_at = end
            lines = lines[:insert_at] + [row] + lines[insert_at:]

    elif args.action == "park":
        lines = update_last_touched(lines, args.date)
        item = args.item.strip()
        for header in ["## Now", "## Next"]:
            start, end = section_bounds(lines, header)
            body = [line for line in lines[start + 2 : end] if line.strip() != f"- {item}"]
            if not body:
                body = ["- None"]
            lines = replace_section_body(lines, header, body)
        start, end = section_bounds(lines, "## Later / Parking Lot")
        body = [line for line in lines[start + 2 : end] if line.strip() != "- None"]
        body.append(f"- {item} — {args.why}")
        lines = replace_section_body(lines, "## Later / Parking Lot", body)
    else:
        raise SystemExit(f"ERROR: unknown action: {args.action}")

    write_text(FOCUS_FILE, "\n".join(lines).rstrip() + "\n")
    print(f"UPDATED={FOCUS_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
