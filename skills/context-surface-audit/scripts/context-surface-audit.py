#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 on this machine.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ANCHORS = (
    "Human Response Contract",
    "Composes With",
    "Progressive Disclosure",
    "Read When Needed",
    "subagent",
    "roadmap",
)
ROOT_SURFACES = (
    "AGENTS.md",
    "claude/CLAUDE.md",
    "README.md",
    "docs/harness-runtime-reference.md",
    "skills/AGENTS.md",
    "skills/README.md",
)


@dataclass
class SurfaceCount:
    path: str
    words: int
    lines: int


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def runtime_home(name: str) -> Path:
    return Path(os.environ.get(f"{name.upper()}_HOME", Path.home() / f".{name}")).expanduser()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_simple_toml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current = data
    for raw_line in read_text(path).splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = data
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip().strip('"')
        raw_value = raw_value.strip()
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            current[key] = [] if not inner else [item.strip().strip('"') for item in inner.split(",")]
        elif raw_value in {"true", "false"}:
            current[key] = raw_value == "true"
        elif raw_value.startswith('"') and raw_value.endswith('"'):
            current[key] = raw_value[1:-1]
        else:
            try:
                current[key] = int(raw_value)
            except ValueError:
                current[key] = raw_value
    return data


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def count_surface(root: Path, rel: str) -> SurfaceCount:
    text = read_text(root / rel)
    return SurfaceCount(rel, word_count(text), len(text.splitlines()))


def skill_counts(root: Path) -> list[SurfaceCount]:
    counts: list[SurfaceCount] = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        counts.append(SurfaceCount(rel, word_count(text), len(text.splitlines())))
    return sorted(counts, key=lambda item: item.words, reverse=True)


def anchor_counts(root: Path) -> dict[str, int]:
    files = [
        *(root.glob("*.md")),
        *(root.glob("docs/**/*.md")),
        *(root.glob("skills/**/*.md")),
    ]
    counts = {anchor: 0 for anchor in ANCHORS}
    for path in files:
        text = read_text(path)
        for anchor in ANCHORS:
            counts[anchor] += text.count(anchor)
    return counts


def load_manifest(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return parse_simple_toml(path)
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def manifest_coverage(root: Path) -> dict[str, Any]:
    manifests = sorted((root / "skills").glob("*/skill.toml"))
    schema_v1: list[str] = []
    missing: list[str] = []
    for manifest in manifests:
        data = load_manifest(manifest)
        name = manifest.parent.name
        if data.get("schema_version") == 1:
            schema_v1.append(name)
        else:
            missing.append(name)
    return {
        "total": len(manifests),
        "schema_v1": len(schema_v1),
        "missing_schema": missing,
    }


def surface_shape(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        return {"path": str(path), "exists": True, "kind": "symlink", "target": os.readlink(path)}
    if path.exists():
        return {"path": str(path), "exists": True, "kind": "copy_or_regular"}
    return {"path": str(path), "exists": False, "kind": "missing"}


def runtime_surfaces() -> dict[str, list[dict[str, Any]]]:
    codex = runtime_home("codex")
    claude = runtime_home("claude")
    return {
        "codex": [
            surface_shape(codex / "AGENTS.md"),
            surface_shape(codex / "config.toml"),
            surface_shape(codex / "hooks.json"),
            surface_shape(codex / "rules"),
            surface_shape(codex / "skills"),
        ],
        "claude": [
            surface_shape(claude / "CLAUDE.md"),
            surface_shape(claude / "settings.json"),
            surface_shape(claude / "statusline-enhanced.sh"),
            surface_shape(claude / "skills"),
        ],
    }


def warnings(root_counts: list[SurfaceCount], skills: list[SurfaceCount], coverage: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in root_counts:
        if item.path == "AGENTS.md" and item.words > 650:
            out.append("AGENTS.md exceeds the soft 650-word root instruction budget.")
        if item.path == "claude/CLAUDE.md" and item.words > 650:
            out.append("claude/CLAUDE.md exceeds the soft 650-word runtime entrypoint budget.")
    if skills and skills[0].words > 2000:
        out.append(f"Largest skill is high-context: {skills[0].path} ({skills[0].words} words).")
    if coverage["missing_schema"]:
        out.append(f"{len(coverage['missing_schema'])} skill manifest(s) do not use schema v1.")
    return out


def audit(root: Path) -> dict[str, Any]:
    roots = [count_surface(root, rel) for rel in ROOT_SURFACES]
    skills = skill_counts(root)
    coverage = manifest_coverage(root)
    return {
        "repo_root": str(root),
        "root_surfaces": [item.__dict__ for item in roots],
        "largest_skills": [item.__dict__ for item in skills[:10]],
        "skill_totals": {
            "count": len(skills),
            "words": sum(item.words for item in skills),
        },
        "duplicate_anchors": anchor_counts(root),
        "manifest_coverage": coverage,
        "runtime_surfaces": runtime_surfaces(),
        "warnings": warnings(roots, skills, coverage),
    }


def print_text(payload: dict[str, Any]) -> None:
    print("Context Surface Audit")
    print(f"Repo: {payload['repo_root']}")
    print()
    print("Root surfaces:")
    for item in payload["root_surfaces"]:
        print(f"- {item['path']}: {item['words']} words, {item['lines']} lines")
    print()
    print("Largest skills:")
    for item in payload["largest_skills"][:8]:
        print(f"- {item['path']}: {item['words']} words, {item['lines']} lines")
    totals = payload["skill_totals"]
    print(f"- total skills: {totals['count']} files, {totals['words']} words")
    print()
    coverage = payload["manifest_coverage"]
    print(f"Manifest schema v1: {coverage['schema_v1']}/{coverage['total']}")
    if coverage["missing_schema"]:
        print("Missing schema:", ", ".join(coverage["missing_schema"]))
    print()
    print("Duplicate anchors:")
    for anchor, count in payload["duplicate_anchors"].items():
        print(f"- {anchor}: {count}")
    print()
    print("Runtime surfaces:")
    for runtime, surfaces in payload["runtime_surfaces"].items():
        print(f"- {runtime}:")
        for surface in surfaces:
            target = f" -> {surface['target']}" if surface.get("target") else ""
            print(f"  - {surface['path']}: {surface['kind']}{target}")
    if payload["warnings"]:
        print()
        print("Warnings:")
        for warning in payload["warnings"]:
            print(f"- {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit dot-agent context surfaces without transcript content.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    args = parser.parse_args()

    payload = audit(args.repo_root.expanduser().resolve())
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
