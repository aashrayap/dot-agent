#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from claude_adapter import load_claude_session
from codex_adapter import load_codex_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default="all", choices=["all", "codex", "claude"])
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--include-subthreads", action="store_true")
    return parser.parse_args()


def _judge_inputs(session: dict) -> dict:
    return {
        "focus": {
            "wall_human": session.get("wall_human"),
            "cwd": session.get("cwd"),
            "subagent_count": session.get("subagent_count"),
            "followup_user_messages": (session.get("response_fit") or {}).get("followup_user_messages"),
        },
        "grounding": {
            "tool_calls": session.get("tool_calls"),
            "first_user_message": session.get("first_user_message"),
        },
        "verification": {
            "edits": session.get("edits"),
            "verifications": session.get("verifications"),
            "exec_failures": session.get("exec_failures"),
        },
        "response_fit": session.get("response_fit"),
        "skill_leverage": {
            "skill_mentions": session.get("skill_mentions"),
            "tool_counts": session.get("tool_counts"),
        },
        "efficiency": {
            "tokens": session.get("tokens"),
            "wall_human": session.get("wall_human"),
            "edits": session.get("edits"),
            "assistant_messages": session.get("assistant_messages"),
        },
    }


def _signals(session: dict) -> list[dict[str, object]]:
    signals: list[dict[str, object]] = []
    if session.get("edits", 0) > 0 and session.get("verifications", 0) == 0:
        signals.append(
            {
                "id": "edit-without-verification",
                "severity": "high",
                "evidence": "Edits were recorded but no verification-like command was detected.",
            }
        )
    if session.get("exec_failures", 0) > 0:
        signals.append(
            {
                "id": "command-failures",
                "severity": "medium",
                "evidence": f"{session['exec_failures']} execution failure(s) were detected.",
            }
        )
    response_fit = session.get("response_fit") or {}
    if response_fit.get("feedback_signals"):
        signals.append(
            {
                "id": "response-fit-feedback",
                "severity": "medium",
                "evidence": f"Follow-up feedback signals detected: {response_fit['feedback_signals']}",
            }
        )
    if session.get("subagent_count", 0) >= 3:
        signals.append(
            {
                "id": "spawn-heavy",
                "severity": "low",
                "evidence": f"{session['subagent_count']} subagent/spawn events were recorded.",
            }
        )
    return signals


def main() -> int:
    args = parse_args()

    session = None
    if args.runtime in {"all", "codex"}:
        session = load_codex_session(args.session_id, include_subthreads=args.include_subthreads)
    if session is None and args.runtime in {"all", "claude"}:
        session = load_claude_session(args.session_id)

    if session is None:
        sys.stderr.write(f"ERROR: session not found: {args.session_id}\n")
        return 1

    payload = {
        "session": session,
        "judge_inputs": _judge_inputs(session),
        "signals": _signals(session),
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
