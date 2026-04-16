#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from review_schema import DOT_AGENT_HOME, excerpt

STATE_ROOT = DOT_AGENT_HOME / "state"
FOCUS_FILE = STATE_ROOT / "collab" / "focus.md"
ROADMAP_FILE = STATE_ROOT / "collab" / "roadmap.md"
PROJECTS_DIR = STATE_ROOT / "projects"


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


def _extract_slug(text: str) -> str | None:
    cleaned = text.strip().lstrip("-").strip()
    if cleaned.lower() in {"none", "none set yet."}:
        return None
    match = re.match(r"([a-z0-9][a-z0-9-]*)", cleaned)
    return match.group(1) if match else None


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
            if len(parts) < 2 or parts[0] == "Status" or parts[1] == "-":
                continue
            status = parts[0].lower()
            item = f"- {parts[1]}"
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


def _project_status(text: str) -> str:
    match = re.search(r"^status:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


def _project_section(text: str, header: str) -> str:
    lines = text.splitlines()
    section_lines = _section(lines, header)
    cleaned = [line for line in section_lines if not line.startswith("|---") and line.strip()]
    return "\n".join(cleaned).strip()


def _candidate_project_slugs(sessions: list[dict[str, Any]], focus_context: dict[str, Any]) -> list[str]:
    slugs: list[str] = []
    for item in (focus_context.get("in_progress") or []) + (focus_context.get("queued") or []):
        slug = _extract_slug(item)
        if slug and slug not in slugs:
            slugs.append(slug)
    for session in sessions:
        cwd = session.get("cwd") or ""
        base = Path(cwd).name
        if base and (PROJECTS_DIR / base).is_dir() and base not in slugs:
            slugs.append(base)
    return slugs[:4]


def load_project_contexts(sessions: list[dict[str, Any]], focus_context: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for slug in _candidate_project_slugs(sessions, focus_context):
        project_dir = PROJECTS_DIR / slug
        project_file = project_dir / "project.md"
        execution_file = project_dir / "execution.md"
        if not project_file.exists():
            continue
        project_text = _read(project_file)
        execution_text = _read(execution_file) if execution_file.exists() else ""
        contexts.append(
            {
                "slug": slug,
                "status": _project_status(project_text),
                "goal": excerpt(_project_section(project_text, "## Goal"), 240),
                "blockers": excerpt(_project_section(project_text, "## Blockers & Constraints"), 220),
                "progress_summary": excerpt(_project_section(execution_text, "## Progress Summary"), 240) if execution_text else "",
                "open_followups": excerpt(_project_section(execution_text, "## Open Follow-ups"), 220) if execution_text else "",
            }
        )
    return contexts
