#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from codex_adapter import fetch_codex_sessions
from claude_adapter import fetch_claude_sessions
from review_schema import DB_PATH, HERMES_FINDINGS_PATH, HISTORY_PATH, STATE_ROOT, format_seconds, parse_window


def main(argv: list[str]) -> int:
    window_spec = argv[1] if len(argv) > 1 else "day"
    try:
        window_hours = parse_window(window_spec)
    except ValueError:
        sys.stderr.write(f"ERROR: invalid window spec: {window_spec}\n")
        return 1

    script_dir = Path(__file__).resolve().parent
    fetch_script = script_dir / "fetch-execution-sessions.py"
    inspect_script = script_dir / "inspect-execution-session.py"
    render_script = script_dir / "render-execution-review.py"
    record_script = script_dir / "record-execution-review.py"
    hermes_script = script_dir / "write-hermes-findings.py"

    codex_sessions = fetch_codex_sessions(window_hours=window_hours)
    claude_sessions = fetch_claude_sessions(window_hours=window_hours)

    print(f"FETCH_SCRIPT={fetch_script}")
    print(f"INSPECT_SCRIPT={inspect_script}")
    print(f"RENDER_SCRIPT={render_script}")
    print(f"RECORD_SCRIPT={record_script}")
    print(f"HERMES_FINDINGS_SCRIPT={hermes_script}")
    print(f"WINDOW_SPEC={window_spec}")
    print(f"WINDOW_HOURS={window_hours}")
    print(f"STATE_ROOT={STATE_ROOT}")
    print(f"REVIEWS_DB={DB_PATH}")
    print(f"HISTORY_FILE={HISTORY_PATH}")
    print(f"HERMES_FINDINGS_FILE={HERMES_FINDINGS_PATH}")
    print()

    print(f"=== EXECUTION REVIEW ACTIVITY (last {window_spec} / {window_hours:g}h) ===")
    print(f"  codex_sessions={len(codex_sessions)}")
    print(f"  claude_sessions={len(claude_sessions)}")
    print(f"  total_sessions={len(codex_sessions) + len(claude_sessions)}")
    print()
    print("Use fetch first; inspect only the sessions with the most wall time, failures, missing verification, or response-fit feedback signals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
