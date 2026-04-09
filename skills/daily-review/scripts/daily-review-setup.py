#!/usr/bin/env python3
"""
daily-review-setup.py

Minimal context loader for the /daily-review skill.

Walks ~/.claude/projects/ and lists every project directory that has
at least one top-level *.jsonl file modified within the window. That is
the ENTIRE injected payload — no timeline, no totals, no session ids.

Everything else is fetched on demand:
  - per-project stats + session enumeration: fan-out subagents via
    fetch-last-day-sessions.py --project <slug>
  - per-logical-project aggregate stats: main context runs
    fetch-last-day-sessions.py --session-ids <ids> --no-turns once per
    cluster after the fan-out returns

Usage:
    daily-review-setup.py              → last 24 hours
    daily-review-setup.py <hours>      → last N hours
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
FETCH_SCRIPT = SCRIPTS_DIR / "fetch-last-day-sessions.py"
INSPECT_SCRIPT = SCRIPTS_DIR / "inspect-session.py"

PROJECTS_DIR = Path(
    os.environ.get("CLAUDE_PROJECTS_DIR", Path.home() / ".claude" / "projects")
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "hours",
        nargs="?",
        default="24",
        help="Window size in hours (integer or float). Default: 24.",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    try:
        hours = float(args.hours)
    except ValueError:
        sys.stderr.write(f"ERROR: hours arg must be numeric, got: {args.hours}\n")
        return 1

    print(f"FETCH_SCRIPT={FETCH_SCRIPT}")
    print(f"INSPECT_SCRIPT={INSPECT_SCRIPT}")
    print(f"WINDOW_HOURS={args.hours}")
    print()

    if not PROJECTS_DIR.is_dir():
        print(f"(projects dir not found: {PROJECTS_DIR})")
        return 0

    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    hits: list[tuple[str, int, datetime]] = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        recent_count = 0
        newest: datetime | None = None
        for jf in project_dir.glob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(jf.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if mtime >= cutoff:
                recent_count += 1
                if newest is None or mtime > newest:
                    newest = mtime
        if recent_count > 0 and newest is not None:
            hits.append((project_dir.name, recent_count, newest))

    if not hits:
        print("(no projects with activity in window)")
        return 0

    # Most recent activity first.
    hits.sort(key=lambda row: row[2], reverse=True)

    print(f"=== PROJECTS WITH ACTIVITY (last {args.hours}h) ===")
    print("  label  sessions  slug")
    for idx, (slug, count, _) in enumerate(hits, start=1):
        print(f"  P{idx:<4}  {count:>8}  {slug}")
    print()
    print(
        "Session counts are approximate (stubs/empty sessions may be dropped "
        "by the subagent's fetch call). Fan out one Explore agent per P label "
        "using the slug."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
