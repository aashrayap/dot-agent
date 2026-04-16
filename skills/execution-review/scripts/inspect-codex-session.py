#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--include-subthreads", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script = Path(__file__).resolve().with_name("inspect-execution-session.py")
    cmd = [
        sys.executable,
        str(script),
        "--runtime",
        "codex",
        "--session-id",
        args.thread_id,
    ]
    if args.include_subthreads:
        cmd.append("--include-subthreads")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
