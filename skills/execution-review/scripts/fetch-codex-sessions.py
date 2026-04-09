#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from codex_sessions import build_aggregate, connect_state_db, parse_window, fetch_spawn_counts, select_threads, summarize_thread


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", default="day", help="day, week, raw hours, or suffixed values like 36h / 7d")
    parser.add_argument("--cwd", help="Restrict to one cwd")
    parser.add_argument("--thread-ids", help="Comma-separated thread ids")
    parser.add_argument("--include-subthreads", action="store_true", help="Include spawned child threads")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        window_hours = parse_window(args.window)
    except ValueError:
        sys.stderr.write(f"ERROR: invalid window spec: {args.window}\n")
        return 1

    thread_ids = [item.strip() for item in (args.thread_ids or "").split(",") if item.strip()]

    conn = connect_state_db()
    try:
        rows = select_threads(
            conn,
            window_hours=window_hours,
            cwd=args.cwd,
            thread_ids=thread_ids or None,
            include_subthreads=args.include_subthreads,
        )
        spawn_counts = fetch_spawn_counts(conn)
    finally:
        conn.close()

    summaries = [summarize_thread(row, spawn_count=spawn_counts.get(row["id"], 0)) for row in rows]
    payload = build_aggregate(summaries)
    payload["selection"] = {
        "window": args.window,
        "window_hours": window_hours,
        "cwd": args.cwd,
        "thread_ids": thread_ids,
        "include_subthreads": args.include_subthreads,
    }

    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
