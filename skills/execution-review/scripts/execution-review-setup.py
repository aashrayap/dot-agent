#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from codex_sessions import format_seconds, parse_window, resolve_state_db, select_threads, connect_state_db


def main(argv: list[str]) -> int:
    window_spec = argv[1] if len(argv) > 1 else "day"
    try:
        window_hours = parse_window(window_spec)
    except ValueError:
        sys.stderr.write(f"ERROR: invalid window spec: {window_spec}\n")
        return 1

    script_dir = Path(__file__).resolve().parent
    fetch_script = script_dir / "fetch-codex-sessions.py"
    inspect_script = script_dir / "inspect-codex-session.py"

    conn = connect_state_db()
    try:
        threads = select_threads(conn, window_hours=window_hours)
    finally:
        conn.close()

    print(f"FETCH_SCRIPT={fetch_script}")
    print(f"INSPECT_SCRIPT={inspect_script}")
    print(f"WINDOW_SPEC={window_spec}")
    print(f"WINDOW_HOURS={window_hours}")
    print(f"STATE_DB={resolve_state_db()}")
    print()

    if not threads:
        print("(no top-level Codex threads in window)")
        return 0

    by_cwd: dict[str, dict[str, object]] = defaultdict(lambda: {"threads": 0, "latest": 0, "first": 0})
    for row in threads:
        entry = by_cwd[row["cwd"]]
        entry["threads"] = int(entry["threads"]) + 1
        entry["latest"] = max(int(entry["latest"]), row["updated_at"])
        if not entry["first"]:
            entry["first"] = row["created_at"]
        else:
            entry["first"] = min(int(entry["first"]), row["created_at"])

    rows = sorted(by_cwd.items(), key=lambda item: (-int(item[1]["threads"]), -int(item[1]["latest"]), item[0]))

    print(f"=== CODEX ACTIVITY (last {window_spec} / {window_hours:g}h) ===")
    print("  label  threads  span     cwd")
    for idx, (cwd, info) in enumerate(rows, start=1):
        first = datetime.fromtimestamp(int(info["first"]), tz=timezone.utc)
        latest = datetime.fromtimestamp(int(info["latest"]), tz=timezone.utc)
        span = max(0, int((latest - first).total_seconds()))
        print(f"  C{idx:<4}  {int(info['threads']):>7}  {format_seconds(span):>7}  {cwd}")
    print()
    print(f"Top-level threads in window: {len(threads)}")
    print("Use fetch first; inspect only the threads with the most wall time, failures, or missing verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
