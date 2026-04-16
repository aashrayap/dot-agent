#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

from review_schema import HERMES_FINDINGS_PATH, iso, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", required=True)
    parser.add_argument("--runtime", default="all")
    parser.add_argument("--title")
    parser.add_argument("--finding", action="append", default=[])
    parser.add_argument("--recommendation", action="append", default=[])
    parser.add_argument("--entry-file", help="JSON file containing a full findings entry")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.entry_file:
        try:
            entry = json.loads(Path(args.entry_file).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"ERROR: failed to read entry file: {exc}\n")
            return 1
    else:
        entry = {
            "id": f"hermes-{uuid4().hex[:12]}",
            "source": "hermes",
            "created_at": iso(utc_now()),
            "window": args.window,
            "runtime": args.runtime,
            "title": args.title or "Hermes findings",
            "findings": args.finding,
            "recommendations": args.recommendation,
        }

    HERMES_FINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HERMES_FINDINGS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")

    json.dump({"success": True, "path": str(HERMES_FINDINGS_PATH), "id": entry.get("id")}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
