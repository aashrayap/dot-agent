#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from review_schema import iso, utc_now
from review_store import record_review_run, report_output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--window", required=True)
    parser.add_argument("--runtime", default="all")
    parser.add_argument("--entry-file", required=True, help="JSON file containing the history entry payload")
    parser.add_argument("--report-file", help="Existing markdown report file to copy into the execution-reviews reports dir")
    parser.add_argument("--report-slug", help="Slug for the copied report filename (without .md)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        history_entry = json.loads(Path(args.entry_file).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"ERROR: failed to read history entry: {exc}\n")
        return 1

    report_path = None
    if args.report_file:
        if not args.report_slug:
            sys.stderr.write("ERROR: --report-slug is required when --report-file is provided\n")
            return 1
        src = Path(args.report_file)
        if not src.is_file():
            sys.stderr.write(f"ERROR: report file not found: {src}\n")
            return 1
        dst = report_output_path(args.report_slug)
        shutil.copyfile(src, dst)
        report_path = str(dst)

    record_review_run(
        review_id=args.review_id,
        window=args.window,
        runtime=args.runtime,
        created_at=iso(utc_now()) or "",
        report_path=report_path,
        history_entry=history_entry,
    )
    output = {
        "success": True,
        "review_id": args.review_id,
        "history_file": str(Path.home() / ".dot-agent" / "state" / "collab" / "execution-reviews" / "history.jsonl"),
        "report_path": report_path,
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
