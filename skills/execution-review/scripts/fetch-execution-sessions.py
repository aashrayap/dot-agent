#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from claude_adapter import fetch_claude_sessions
from codex_adapter import fetch_codex_sessions
from review_schema import aggregate_normalized_sessions, parse_window
from review_store import load_matching_hermes_findings, upsert_normalized_sessions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default="all", choices=["all", "codex", "claude"])
    parser.add_argument("--window", default="day", help="day, week, raw hours, or suffixed values like 36h / 7d")
    parser.add_argument("--cwd", help="Restrict Codex sessions to one cwd")
    parser.add_argument("--thread-ids", help="Codex thread ids, comma-separated")
    parser.add_argument("--session-ids", help="Claude session ids, comma-separated")
    parser.add_argument("--include-subthreads", action="store_true", help="Include Codex spawned child threads")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        window_hours = parse_window(args.window)
    except ValueError:
        sys.stderr.write(f"ERROR: invalid window spec: {args.window}\n")
        return 1

    records: list[dict] = []
    if args.runtime in {"all", "codex"}:
        thread_ids = [item.strip() for item in (args.thread_ids or "").split(",") if item.strip()]
        records.extend(
            fetch_codex_sessions(
                window_hours=window_hours,
                cwd=args.cwd,
                thread_ids=thread_ids or None,
                include_subthreads=args.include_subthreads,
            )
        )
    if args.runtime in {"all", "claude"}:
        session_ids = [item.strip() for item in (args.session_ids or "").split(",") if item.strip()]
        records.extend(
            fetch_claude_sessions(
                window_hours=window_hours,
                session_ids=session_ids or None,
            )
        )

    upsert_normalized_sessions(records)
    payload = aggregate_normalized_sessions(records)
    payload["selection"] = {
        "runtime": args.runtime,
        "window": args.window,
        "window_hours": window_hours,
        "cwd": args.cwd,
        "thread_ids": [item.strip() for item in (args.thread_ids or "").split(",") if item.strip()],
        "session_ids": [item.strip() for item in (args.session_ids or "").split(",") if item.strip()],
        "include_subthreads": args.include_subthreads,
    }
    payload["hermes_findings"] = load_matching_hermes_findings(args.window, args.runtime)

    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
