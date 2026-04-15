#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--why", required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--queued", action="append", default=[])
    parser.add_argument("--done", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dot_agent = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
    projects_setup = dot_agent / "skills" / "projects" / "scripts" / "projects-setup.sh"
    focus_update = dot_agent / "skills" / "focus" / "scripts" / "focus-update.py"

    setup_result = subprocess.run(
        ["bash", str(projects_setup), "--ensure-execution", args.slug],
        check=True,
        capture_output=True,
        text=True,
    )

    cmd = [
        sys.executable,
        str(focus_update),
        "set",
        "--date",
        args.date,
        "--current",
        args.slug,
        "--why",
        args.why,
        "--now",
        f"{args.slug} — promoted into active tracked project focus",
    ]
    for item in args.queued:
        cmd.extend(["--next", item])
    for item in args.done:
        cmd.extend(["--later", item])
    subprocess.run(cmd, check=True)
    sys.stdout.write(setup_result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
