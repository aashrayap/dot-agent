#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from review_schema import DOT_AGENT_HOME

STATE_ROOT = DOT_AGENT_HOME / "state"
FOCUS_FILE = STATE_ROOT / "collab" / "focus.md"
ROADMAP_FILE = STATE_ROOT / "collab" / "roadmap.md"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _section(lines: list[str], header: str) -> list[str]:
    try:
        start = lines.index(header)
    except ValueError:
        return []
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != header:
            end = idx
            break
    return [line for line in lines[start + 1 : end] if line.strip()]


def load_focus_context() -> dict[str, Any]:
    if ROADMAP_FILE.exists():
        lines = _read(ROADMAP_FILE).splitlines()
        focus = " ".join(_section(lines, "## Focus")).strip()
        in_progress: list[str] = []
        queued: list[str] = []
        done: list[str] = []
        blockers: list[str] = []
        for line in lines:
            if not line.startswith("|"):
                continue
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            if len(parts) < 5 or parts[0] in {"Project", "---------"} or parts[2] == "-":
                continue
            status = parts[1].lower()
            item = f"- {parts[0]}: {parts[2]}"
            if status == "in progress":
                in_progress.append(item)
            elif status == "queued":
                queued.append(item)
            elif status == "completed":
                done.append(item)
            elif status == "blocked":
                blockers.append(item)
        return {
            "exists": True,
            "path": str(ROADMAP_FILE),
            "legacy_focus_path": str(FOCUS_FILE),
            "current_focus": focus,
            "focus": focus,
            "now": in_progress,
            "next": queued,
            "later": [],
            "blockers": blockers,
            "queued": queued + blockers,
            "in_progress": in_progress,
            "done": done,
        }

    if not FOCUS_FILE.exists():
        return {"exists": False, "path": str(FOCUS_FILE)}
    lines = _read(FOCUS_FILE).splitlines()
    if "## Current Focus" in lines:
        current_focus = " ".join(_section(lines, "## Current Focus")).strip()
        now = [line.strip() for line in _section(lines, "## Now") if line.strip() != "- None"]
        next_items = [line.strip() for line in _section(lines, "## Next") if line.strip() != "- None"]
        later = [line.strip() for line in _section(lines, "## Later / Parking Lot") if line.strip() != "- None"]
        blockers = [line.strip() for line in _section(lines, "## Blockers") if line.strip() != "- None"]
        return {
            "exists": True,
            "path": str(FOCUS_FILE),
            "current_focus": current_focus,
            "focus": current_focus,
            "now": now,
            "next": next_items,
            "later": later,
            "blockers": blockers,
            "in_progress": now,
            "queued": next_items + later + blockers,
            "done": [],
        }

    focus = " ".join(_section(lines, "## Focus")).strip()
    queued = [line.strip() for line in _section(lines, "## Queued") if line.strip() != "- None"]
    in_progress = [line.strip() for line in _section(lines, "## In Progress") if line.strip() != "- None"]
    done = [line.strip() for line in _section(lines, "## Done") if line.strip() != "- None"]
    return {
        "exists": True,
        "path": str(FOCUS_FILE),
        "current_focus": in_progress[0] if in_progress else focus,
        "focus": focus,
        "now": in_progress,
        "next": queued,
        "later": [],
        "blockers": [],
        "queued": queued,
        "in_progress": in_progress,
        "done": done,
    }
