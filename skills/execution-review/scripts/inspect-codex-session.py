#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from codex_sessions import connect_state_db, fetch_spawn_counts, select_threads, summarize_thread


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", required=True, help="Full Codex thread id")
    parser.add_argument("--include-subthreads", action="store_true", help="Allow direct inspection of a spawned child thread")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    conn = connect_state_db()
    try:
        rows = select_threads(
            conn,
            thread_ids=[args.thread_id],
            include_subthreads=args.include_subthreads,
        )
        spawn_counts = fetch_spawn_counts(conn)
    finally:
        conn.close()

    if not rows:
        sys.stderr.write(f"ERROR: thread not found or excluded: {args.thread_id}\n")
        return 1

    summary = summarize_thread(rows[0], spawn_count=spawn_counts.get(rows[0]["id"], 0), include_timeline=True)

    signals: list[dict[str, object]] = []
    if summary["signals"]["edit_without_verification"]:
        signals.append(
            {
                "id": "edit-without-verification",
                "severity": "high",
                "evidence": "apply_patch was used but no verification-like command was recorded.",
            }
        )
    if summary["exec_failures"] > 0:
        signals.append(
            {
                "id": "command-failures",
                "severity": "medium",
                "evidence": f"{summary['exec_failures']} command(s) exited non-zero.",
            }
        )
    if summary["signals"]["heavy_read_before_action"]:
        signals.append(
            {
                "id": "heavy-read-before-action",
                "severity": "medium",
                "evidence": "Many read-style commands were used without any edit, which may be fine for research but should be judged for decisiveness.",
            }
        )
    if summary["spawned_threads"] >= 3:
        signals.append(
            {
                "id": "spawn-heavy",
                "severity": "low",
                "evidence": f"{summary['spawned_threads']} child thread(s) were spawned.",
            }
        )

    payload = {
        "thread": summary,
        "judge_inputs": {
            "focus": {
                "wall_human": summary["wall_human"],
                "cwd": summary["cwd"],
                "spawned_threads": summary["spawned_threads"],
            },
            "grounding": {
                "read_commands": summary["read_commands"],
                "web_search_calls": summary["web_search_calls"],
                "first_user_message": summary["first_user_message"],
            },
            "depth": {
                "user_messages": summary["user_messages"],
                "agent_messages": summary["agent_messages"],
                "apply_patches": summary["apply_patches"],
                "function_calls": summary["function_calls"],
            },
            "verification": {
                "verification_commands": summary["verification_commands"],
                "exec_failures": summary["exec_failures"],
            },
            "closure": {
                "final_messages": summary["final_messages"],
                "timeline_tail": summary.get("timeline", [])[-5:],
            },
        },
        "signals": signals,
    }

    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
