#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 on this machine.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        import toml_compat as tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


KNOWN_TARGETS = {"claude", "codex"}
SCHEMA_VERSION = 1
COMPOSITION_ARRAYS = (
    "parents",
    "children",
    "formats",
    "reads",
    "writes",
    "delegates",
    "handoffs",
)
CONTRACT_ARRAYS = (
    "inputs",
    "outputs",
    "scripts",
    "references",
    "assets",
    "state_reads",
    "state_writes",
    "tools",
)
INVOKE_ARRAYS = ("explicit",)
LOCAL_SKILL_FIELDS = ("parents", "children", "formats", "delegates", "handoffs")
EXTERNAL_PREFIXES = ("github:", "plugin:", "app:", "external:")


@dataclass
class Finding:
    severity: str
    skill: str
    message: str


@dataclass
class Result:
    checked_skills: int = 0
    schema_v1_skills: int = 0
    findings: list[Finding] = field(default_factory=list)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_toml(path: Path, result: Result, skill: str) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
            if isinstance(data, dict):
                return data
    except tomllib.TOMLDecodeError as exc:
        result.findings.append(Finding("ERROR", skill, f"invalid TOML: {exc}"))
    except OSError as exc:
        result.findings.append(Finding("ERROR", skill, f"cannot read skill.toml: {exc}"))
    return {}


def frontmatter_name(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def runtime_entry(runtime: str, manifest: dict[str, Any]) -> str:
    specific = manifest.get(f"{runtime}_entry")
    if isinstance(specific, str) and specific:
        return specific
    default = manifest.get("default_entry")
    if isinstance(default, str) and default:
        return default
    return "SKILL.md"


def add(result: Result, severity: str, skill: str, message: str) -> None:
    result.findings.append(Finding(severity, skill, message))


def require_string_list(
    result: Result,
    *,
    skill: str,
    table_name: str,
    table: dict[str, Any],
    keys: tuple[str, ...],
) -> None:
    for key in keys:
        value = table.get(key)
        if value is None:
            add(result, "ERROR", skill, f"missing [{table_name}].{key}")
            continue
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            add(result, "ERROR", skill, f"[{table_name}].{key} must be a string array")


def check_declared_paths(
    result: Result,
    *,
    skill: str,
    skill_dir: Path,
    table: dict[str, Any],
    key: str,
) -> None:
    values = table.get(key, [])
    if not isinstance(values, list):
        return
    for rel in values:
        if not isinstance(rel, str) or not rel:
            continue
        if rel.startswith(("~", "/", "state/", "docs/")):
            continue
        if not (skill_dir / rel).exists():
            add(result, "ERROR", skill, f"declared {key} path does not exist: {rel}")


def normalized_skill_ref(value: str) -> str:
    value = value.strip().strip("`")
    if not value or value.lower() == "none":
        return ""
    if value.endswith(".py") or "/" in value or value.startswith(EXTERNAL_PREFIXES):
        return ""
    if " " in value or "," in value or ";" in value:
        return ""
    return value


def check_local_skill_refs(
    result: Result,
    *,
    skill: str,
    composition: dict[str, Any],
    known_skills: set[str],
) -> None:
    for key in LOCAL_SKILL_FIELDS:
        values = composition.get(key, [])
        if not isinstance(values, list):
            continue
        for raw in values:
            if not isinstance(raw, str):
                continue
            ref = normalized_skill_ref(raw)
            if ref and ref not in known_skills:
                add(result, "ERROR", skill, f"[composition].{key} references unknown skill: {ref}")


def check_skill(skill_dir: Path, known_skills: set[str], result: Result) -> None:
    skill = skill_dir.name
    manifest_path = skill_dir / "skill.toml"
    root_skill_md = skill_dir / "SKILL.md"

    if not manifest_path.is_file() and not root_skill_md.is_file():
        return

    result.checked_skills += 1

    if not manifest_path.is_file():
        add(result, "ERROR", skill, "missing skill.toml")
        return
    if not root_skill_md.is_file():
        add(result, "ERROR", skill, "missing SKILL.md")
        return

    manifest = load_toml(manifest_path, result, skill)
    if not manifest:
        return

    name = manifest.get("name")
    if name != skill:
        add(result, "ERROR", skill, f"skill.toml name must equal folder name ({skill})")

    root_text = read_text(root_skill_md)
    if frontmatter_name(root_text) != skill:
        add(result, "ERROR", skill, f"SKILL.md frontmatter name must equal {skill}")
    if "## Composes With" not in root_text:
        add(result, "ERROR", skill, "SKILL.md missing ## Composes With")

    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets or any(not isinstance(item, str) for item in targets):
        add(result, "ERROR", skill, "targets must be a non-empty string array")
        targets = []
    for target in targets:
        if target not in KNOWN_TARGETS:
            add(result, "ERROR", skill, f"unknown target: {target}")
            continue
        entry = runtime_entry(target, manifest)
        entry_path = skill_dir / entry
        if not entry_path.is_file():
            add(result, "ERROR", skill, f"missing {target} entry: {entry}")
            continue
        entry_name = frontmatter_name(read_text(entry_path))
        if entry_name and entry_name != skill:
            add(result, "ERROR", skill, f"{target} entry frontmatter name must equal {skill}: {entry}")

    schema_version = manifest.get("schema_version")
    if schema_version is None:
        add(result, "WARN", skill, "missing schema_version; v1 schema not adopted")
        return
    if schema_version != SCHEMA_VERSION:
        add(result, "ERROR", skill, f"unsupported schema_version: {schema_version}")
        return

    result.schema_v1_skills += 1
    composition = manifest.get("composition")
    contract = manifest.get("contract")
    invoke = manifest.get("invoke")

    if not isinstance(composition, dict):
        add(result, "ERROR", skill, "missing [composition] table")
        composition = {}
    if not isinstance(contract, dict):
        add(result, "ERROR", skill, "missing [contract] table")
        contract = {}
    if not isinstance(invoke, dict):
        add(result, "ERROR", skill, "missing [invoke] table")
        invoke = {}

    require_string_list(result, skill=skill, table_name="composition", table=composition, keys=COMPOSITION_ARRAYS)
    require_string_list(result, skill=skill, table_name="contract", table=contract, keys=CONTRACT_ARRAYS)
    require_string_list(result, skill=skill, table_name="invoke", table=invoke, keys=INVOKE_ARRAYS)

    implicit = invoke.get("implicit")
    if not isinstance(implicit, bool):
        add(result, "ERROR", skill, "[invoke].implicit must be boolean")

    check_local_skill_refs(result, skill=skill, composition=composition, known_skills=known_skills)
    for key in ("scripts", "references", "assets"):
        check_declared_paths(result, skill=skill, skill_dir=skill_dir, table=contract, key=key)


def validate(root: Path) -> Result:
    skills_root = root / "skills"
    result = Result()
    skill_dirs = sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    known_skills = {path.name for path in skill_dirs}

    for skill_dir in skill_dirs:
        check_skill(skill_dir, known_skills, result)

    return result


def as_dict(result: Result) -> dict[str, Any]:
    return {
        "checked_skills": result.checked_skills,
        "schema_v1_skills": result.schema_v1_skills,
        "findings": [finding.__dict__ for finding in result.findings],
    }


def print_text(result: Result) -> None:
    print("Skill Manifest Validation")
    print(f"Checked {result.checked_skills} skills; {result.schema_v1_skills} use schema v1.")
    if not result.findings:
        print("OK: no manifest issues found.")
        return
    for finding in result.findings:
        print(f"{finding.severity}: {finding.skill}: {finding.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate dot-agent skill manifests.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on WARN findings.")
    args = parser.parse_args()

    result = validate(repo_root())
    if args.format == "json":
        print(json.dumps(as_dict(result), indent=2, sort_keys=True))
    else:
        print_text(result)

    if any(finding.severity == "ERROR" for finding in result.findings):
        return 1
    if args.strict and any(finding.severity == "WARN" for finding in result.findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
