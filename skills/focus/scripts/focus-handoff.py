#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", str(Path.home() / ".dot-agent"))).expanduser()
DOT_AGENT_STATE_HOME = Path(
    os.environ.get("DOT_AGENT_STATE_HOME", str(DOT_AGENT_HOME / "state"))
).expanduser()
FOCUS_FILE = DOT_AGENT_STATE_HOME / "collab" / "focus.md"
ROADMAP_FILE = DOT_AGENT_STATE_HOME / "collab" / "roadmap.md"
PROJECTS_DIR = DOT_AGENT_STATE_HOME / "projects"


@dataclass(frozen=True)
class ProjectMatch:
    slug: str
    source: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}")


def section_body(lines: list[str], header: str) -> list[str]:
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise SystemExit(f"ERROR: missing section {header!r} in {FOCUS_FILE}") from exc
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


def roadmap_active_row() -> tuple[str, str]:
    if not ROADMAP_FILE.exists():
        return "", ""
    in_active = False
    for line in read_text(ROADMAP_FILE).splitlines():
        if line == "## Active Projects":
            in_active = True
            continue
        if in_active and line.startswith("## "):
            break
        if not in_active:
            continue
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) >= 5 and parts[0] not in {"Project", "---------"}:
            if parts[1].lower() == "in progress" and parts[2] not in {"Task", "-"}:
                return parts[0], parts[2]
    return "", ""


def normalize(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered


def project_status(project_file: Path) -> str:
    for line in read_text(project_file).splitlines()[:10]:
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def active_projects() -> list[str]:
    slugs: list[str] = []
    if not PROJECTS_DIR.is_dir():
        return slugs
    for entry in sorted(PROJECTS_DIR.iterdir()):
        project_file = entry / "project.md"
        if not project_file.is_file():
            continue
        if project_status(project_file) == "complete":
            continue
        slugs.append(entry.name)
    return slugs


def exact_slug_match(value: str, slugs: list[str], source: str) -> ProjectMatch | None:
    normalized = normalize(value)
    for slug in slugs:
        if normalized == slug:
            return ProjectMatch(slug=slug, source=source)
    return None


def substring_slug_matches(value: str, slugs: list[str], source: str) -> list[ProjectMatch]:
    normalized = normalize(value)
    matches: list[ProjectMatch] = []
    for slug in slugs:
        if slug in normalized:
            matches.append(ProjectMatch(slug=slug, source=source))
    return matches


def shell_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n")


def main() -> int:
    allow_project_state = os.environ.get("FOCUS_HANDOFF_ALLOW_PROJECTS") == "1"
    current_focus = roadmap_focus()
    roadmap_project, now_item = roadmap_active_row()
    if not current_focus and FOCUS_FILE.exists():
        lines = read_text(FOCUS_FILE).splitlines()
        current_focus = first_nonempty_line(section_body(lines, "## Current Focus"))
        now_item = first_list_item(section_body(lines, "## Now"))
    slugs = active_projects() if allow_project_state else []

    exact_match = exact_slug_match(roadmap_project, slugs, "roadmap-project")
    if exact_match is None:
        exact_match = exact_slug_match(current_focus, slugs, "current-focus")
    if exact_match is None:
        exact_match = exact_slug_match(now_item, slugs, "now-item")

    contains_matches: list[ProjectMatch] = []
    unique_contains: ProjectMatch | None = None
    if exact_match is None:
        contains_matches = substring_slug_matches(current_focus, slugs, "current-focus")
        if not contains_matches and now_item:
            contains_matches = substring_slug_matches(now_item, slugs, "now-item")
        unique_slugs = sorted({match.slug for match in contains_matches})
        if len(unique_slugs) == 1:
            unique_contains = ProjectMatch(slug=unique_slugs[0], source=contains_matches[0].source)

    project_match = exact_match or unique_contains

    print(f"ROADMAP_FILE={ROADMAP_FILE}")
    print(f"FOCUS_FILE={FOCUS_FILE}")
    print(f"CURRENT_FOCUS={shell_quote(current_focus or 'None set yet.')}")
    print(f"ROADMAP_ACTIVE_PROJECT={shell_quote(roadmap_project or 'General')}")
    print(f"NOW_ITEM={shell_quote(now_item or 'None')}")
    print(f"PROJECT_STATE_NORMAL_READS={'yes' if allow_project_state else 'no'}")
    print(f"ACTIVE_PROJECTS={','.join(slugs)}")

    if not allow_project_state:
        print("PROJECT_MATCH=")
        print("MATCH_SOURCE=")
        print("MATCH_CONFIDENCE=none")
        print("PROJECT_READY=no")
        print("PROJECT_REASON=Project handoff is explicit only; normal focus stays on the human roadmap.")
        print("SUGGESTED_PROJECTS_COMMAND=")
    elif project_match is None:
        print("PROJECT_MATCH=")
        print("MATCH_SOURCE=")
        print("MATCH_CONFIDENCE=none")
        print("PROJECT_READY=no")
        if len({match.slug for match in contains_matches}) > 1:
            print("PROJECT_REASON=Focus text mentions multiple tracked projects; stay in focus until one project is explicit.")
        else:
            print("PROJECT_REASON=Focus does not map cleanly to one tracked project.")
        print("SUGGESTED_PROJECTS_COMMAND=")
    else:
        confidence = "exact" if exact_match is not None else "contains"
        print(f"PROJECT_MATCH={project_match.slug}")
        print(f"MATCH_SOURCE={project_match.source}")
        print(f"MATCH_CONFIDENCE={confidence}")
        print("PROJECT_READY=yes")
        print(
            f"PROJECT_REASON=Focus maps to tracked project '{project_match.slug}'. "
            "Use the projects skill when transitioning from prioritization into project execution."
        )
        print(f"SUGGESTED_PROJECTS_COMMAND=projects {project_match.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
