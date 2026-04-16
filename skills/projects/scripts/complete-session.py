#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir")
    parser.add_argument("--date", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--ref", default="")
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}")


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to write {path}: {exc}")


def section_bounds(lines: list[str], header: str) -> tuple[int, int]:
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise SystemExit(f"ERROR: missing section {header!r}") from exc
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != header:
            end = idx
            break
    return start, end


def update_last_touched(lines: list[str], date_value: str) -> list[str]:
    out: list[str] = []
    for line in lines:
        if line.startswith("last_touched:"):
            out.append(f"last_touched: {date_value}")
        else:
            out.append(line)
    return out


def extract_session_block(lines: list[str], section_header: str, session_id: str) -> tuple[list[str], str | None]:
    start, end = section_bounds(lines, section_header)
    target = f"#### <a id=\"{session_id.lower()}\"></a>{session_id} — "
    idx = None
    for i in range(start + 1, end):
        if lines[i].startswith(target):
            idx = i
            break
    if idx is None:
        return lines, None
    block_end = end
    for j in range(idx + 1, end):
        if lines[j].startswith("#### <a id="):
            block_end = j
            break
    header_line = lines[idx]
    session_name = header_line.split("—", 1)[1].strip() if "—" in header_line else session_id
    new_lines = lines[:idx] + lines[block_end:]
    return new_lines, session_name


def extract_current_slice(lines: list[str]) -> tuple[list[str], str | None]:
    start, end = section_bounds(lines, "## Current Slice")
    body = [line.strip() for line in lines[start + 1 : end] if line.strip()]
    if not body:
        return lines, None
    session_name = " ".join(body)
    new_lines = lines[: start + 1] + ["", "None"] + lines[end:]
    return new_lines, session_name


def append_completed_row(lines: list[str], session_name: str, date_value: str, ref: str) -> list[str]:
    try:
        _, end = section_bounds(lines, "## Completed")
        row = f"| {session_name} | {date_value} | {ref} |"
    except SystemExit:
        _, end = section_bounds(lines, "## Done")
        row = f"| {date_value} | {session_name} | {ref} |"
    return lines[:end] + [row] + lines[end:]


def remove_mermaid_refs(lines: list[str], session_id: str) -> list[str]:
    needle = session_id.lower()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if f"{needle}([" in stripped:
            continue
        if stripped.startswith("style ") and needle in stripped:
            continue
        if needle in stripped and "-->" in stripped:
            continue
        out.append(line)
    return out


def append_audit(audit_log: Path, session_id: str, session_name: str, date_value: str, ref: str, outcome: str, notes: str) -> None:
    text = read_text(audit_log)
    text += (
        f"\n## {date_value}\n\n"
        f"Completed {session_id} — {session_name}.\n\n"
        f"- Outcome: {outcome}\n"
        f"- Ref: {ref or 'n/a'}\n"
        f"- Notes: {notes or 'n/a'}\n"
    )
    write_text(audit_log, text)


def update_execution(project_dir: Path, session_name: str, date_value: str, ref: str, outcome: str, notes: str) -> None:
    dot_agent = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
    projects_setup = dot_agent / "skills" / "projects" / "scripts" / "projects-setup.sh"
    update_execution_script = dot_agent / "skills" / "projects" / "scripts" / "update-execution.py"

    subprocess.run(
        ["bash", str(projects_setup), "--ensure-execution", project_dir.name],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            sys.executable,
            str(update_execution_script),
            str(project_dir),
            "session",
            "--date",
            date_value,
            "--session",
            session_name,
            "--outcome",
            outcome,
            "--ref",
            ref,
            "--notes",
            notes,
        ],
        check=True,
    )


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser()
    project_file = project_dir / "project.md"
    audit_log = project_dir / "AUDIT_LOG.md"
    if not project_file.exists():
        raise SystemExit(f"ERROR: project file not found: {project_file}")

    lines = read_text(project_file).splitlines()
    lines = update_last_touched(lines, args.date)
    lines, session_name = extract_session_block(lines, "## Available Sessions", args.session_id)
    if session_name is None:
        lines, session_name = extract_session_block(lines, "## Blocked Sessions", args.session_id)
    if session_name is None:
        lines, session_name = extract_current_slice(lines)
    if session_name is None:
        raise SystemExit(f"ERROR: session {args.session_id} not found and Current Slice is empty")
    lines = append_completed_row(lines, f"{args.session_id} — {session_name}", args.date, args.ref)
    lines = remove_mermaid_refs(lines, args.session_id)
    write_text(project_file, "\n".join(lines).rstrip() + "\n")
    if audit_log.exists():
        append_audit(audit_log, args.session_id, session_name, args.date, args.ref, args.outcome, args.notes)
    update_execution(project_dir, f"{args.session_id} — {session_name}", args.date, args.ref, args.outcome, args.notes)
    print(f"UPDATED={project_file}")
    if audit_log.exists():
        print(f"AUDIT_LOG={audit_log}")
    print(f"EXECUTION_FILE={project_dir / 'execution.md'}")
    print(f"SESSION_NAME={session_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
