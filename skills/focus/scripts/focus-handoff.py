#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
DOT_AGENT_STATE_HOME = Path(
    os.environ.get("DOT_AGENT_STATE_HOME", str(DOT_AGENT_HOME / "state"))
).expanduser()
FOCUS_FILE = DOT_AGENT_STATE_HOME / "collab" / "focus.md"
ROADMAP_FILE = DOT_AGENT_STATE_HOME / "collab" / "roadmap.md"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}") from exc


def section_body(lines: list[str], header: str, path: Path) -> list[str]:
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise SystemExit(f"ERROR: missing section {header!r} in {path}") from exc
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != header:
            end = idx
            break
    return lines[start + 1 : end]


def first_nonempty_line(lines: list[str]) -> str:
    for line in lines:
        value = line.strip()
        if value:
            return value
    return ""


def first_list_item(lines: list[str]) -> str:
    for line in lines:
        value = line.strip()
        if value.startswith("- "):
            item = value[2:].strip()
            if item and item.lower() != "none":
                return item
    return ""


def roadmap_focus() -> str:
    if not ROADMAP_FILE.exists():
        return ""
    lines = read_text(ROADMAP_FILE).splitlines()
    try:
        start = lines.index("## Focus")
    except ValueError:
        return ""
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.strip():
            body.append(line.strip())
    return " ".join(body)


def roadmap_active_row() -> tuple[str, str, str]:
    if not ROADMAP_FILE.exists():
        return "", "", ""
    in_active = False
    for line in read_text(ROADMAP_FILE).splitlines():
        if line == "## Active Projects":
            in_active = True
            continue
        if in_active and line.startswith("## "):
            break
        if not in_active or not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) >= 5 and parts[0] not in {"Project", "---------"}:
            if parts[1].lower() == "in progress" and parts[2] not in {"Task", "-"}:
                return parts[0], parts[1], parts[2]
    return "", "", ""


def shell_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n")


def main() -> int:
    current_focus = roadmap_focus()
    workstream, status, task = roadmap_active_row()
    if not current_focus and FOCUS_FILE.exists():
        lines = read_text(FOCUS_FILE).splitlines()
        current_focus = first_nonempty_line(section_body(lines, "## Current Focus", FOCUS_FILE))
        task = first_list_item(section_body(lines, "## Now", FOCUS_FILE))
        workstream = workstream or "General"
        status = status or "In Progress"

    suggested_surface = "focus"
    reason = "Stay on the human roadmap until the user asks for deeper planning."
    lowered = " ".join([current_focus, workstream, task]).lower()
    if any(term in lowered for term in ["spec", "implementation", "design", "research", "tasks"]):
        suggested_surface = "spec-new-feature"
        reason = "The active row appears to need code-grounded planning."
    elif any(term in lowered for term in ["idea", "concept", "brief", "incubat"]):
        suggested_surface = "idea"
        reason = "The active row appears conceptual."

    print(f"ROADMAP_FILE={ROADMAP_FILE}")
    print(f"FOCUS_FILE={FOCUS_FILE}")
    print(f"CURRENT_FOCUS={shell_quote(current_focus or 'None set yet.')}")
    print(f"ROADMAP_ACTIVE_WORKSTREAM={shell_quote(workstream or 'General')}")
    print(f"ROADMAP_ACTIVE_STATUS={shell_quote(status or 'None')}")
    print(f"NOW_ITEM={shell_quote(task or 'None')}")
    print(f"SUGGESTED_SURFACE={suggested_surface}")
    print(f"HANDOFF_REASON={reason}")
    print("DEEP_STATE_NORMAL_READS=no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
