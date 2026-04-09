#!/usr/bin/env python3
"""Block parent 2026 wiki commits unless the user confirms the target repo."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PARENT_REPO = Path("/Users/ash/Documents/2026")
SEMI_WIKI = Path("/Users/ash/Documents/2026/semi-stocks/wiki")
OVERRIDE_ENV = "ALLOW_2026_WIKI_COMMIT"
COMMIT_RE = re.compile(r"(^|[;&|(]\s*)git\s+commit(?:\s|$)")


def run_git(cwd: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", cwd, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    if os.environ.get(OVERRIDE_ENV) == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    command = ((payload.get("tool_input") or {}).get("command") or "").strip()
    if not COMMIT_RE.search(command):
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    try:
        repo_root = Path(run_git(cwd, "rev-parse", "--show-toplevel")).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0

    if repo_root != PARENT_REPO:
        return 0

    try:
        staged = run_git(
            cwd,
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMR",
            "--",
            "wiki",
        )
    except subprocess.CalledProcessError:
        return 0

    staged_files = [line.strip() for line in staged.splitlines() if line.strip().startswith("wiki/")]
    if not staged_files:
        return 0

    preview = ", ".join(staged_files[:3])
    if len(staged_files) > 3:
        preview += ", ..."

    reason = (
        "Staged parent 2026 wiki changes detected "
        f"({preview}). If this work was meant for semi-stocks, write it to {SEMI_WIKI} "
        f"instead. Re-run with {OVERRIDE_ENV}=1 git commit ... to confirm the parent wiki "
        "is intentional."
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
