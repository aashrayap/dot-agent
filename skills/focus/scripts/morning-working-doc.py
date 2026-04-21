#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
DOT_AGENT_STATE_HOME = Path(os.environ.get("DOT_AGENT_STATE_HOME", str(DOT_AGENT_HOME / "state"))).expanduser()
MORNING_DIR = DOT_AGENT_STATE_HOME / "collab" / "morning"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create one approved morning focus working document.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--title", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--next-step", required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--doc", action="append", default=[], help="Important supporting doc path or URL")
    parser.add_argument("--write", action="store_true", help="Write the document. Without this, print a dry run.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing dated document.")
    return parser.parse_args()


def clean_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "/")


def doc_path(raw_date: str) -> Path:
    try:
        date.fromisoformat(raw_date)
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid --date {raw_date!r}; expected YYYY-MM-DD") from exc
    return MORNING_DIR / f"{raw_date}.md"


def render(args: argparse.Namespace) -> str:
    evidence = args.evidence or ["-"]
    docs = args.doc or ["-"]
    lines = [
        "---",
        f"date: {args.date}",
        "status: draft",
        "---",
        "",
        f"# {args.title}",
        "",
        "## Goal",
        "",
        args.goal.strip(),
        "",
        "## Evidence",
        "",
        *[f"- {clean_cell(item)}" for item in evidence],
        "",
        "## Important Docs",
        "",
        *[f"- {item.strip()}" for item in docs],
        "",
        "## Next Step",
        "",
        args.next_step.strip(),
        "",
        "## Gate",
        "",
        args.gate.strip(),
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    output = render(args)
    path = doc_path(args.date)
    if not args.write:
        print(f"DRY_RUN_PATH={path}")
        print(output)
        return 0
    if path.exists() and not args.force:
        raise SystemExit(f"ERROR: {path} exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    print(f"WROTE={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
