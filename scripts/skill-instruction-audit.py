#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DANGLING_SOURCE_REFS = (
    "skills/AGENTS.md",
    "`skills/AGENTS.md`",
)
SHARED_DIRS = ("scripts", "assets", "references", "shared")


@dataclass
class Finding:
    severity: str
    skill: str
    runtime: str
    message: str


@dataclass
class AuditResult:
    checked_skills: int = 0
    checked_payloads: int = 0
    findings: list[Finding] = field(default_factory=list)


def dot_agent_home() -> Path:
    return Path(os.environ.get("DOT_AGENT_HOME", Path(__file__).resolve().parents[1])).expanduser()


def runtime_home(name: str) -> Path:
    env_name = f"{name.upper()}_HOME"
    default = Path.home() / f".{name}"
    return Path(os.environ.get(env_name, default)).expanduser()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def manifest_targets(skill_dir: Path, manifest: dict[str, Any]) -> list[str]:
    raw = manifest.get("targets")
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if (skill_dir / "SKILL.md").is_file():
        return ["claude"]
    return []


def runtime_entry(runtime: str, manifest: dict[str, Any]) -> str:
    specific = manifest.get(f"{runtime}_entry")
    if isinstance(specific, str) and specific:
        return specific
    default = manifest.get("default_entry")
    if isinstance(default, str) and default:
        return default
    return "SKILL.md"


def has_dangling_source_ref(text: str) -> bool:
    return any(ref in text for ref in DANGLING_SOURCE_REFS)


def expected_payload_root(runtime: str, skill_name: str) -> Path:
    return runtime_home(runtime) / "skills" / skill_name


def audit_skill_runtime(
    result: AuditResult,
    *,
    skill_dir: Path,
    skill_name: str,
    runtime: str,
    entry: str,
) -> None:
    source_entry = skill_dir / entry
    payload_root = expected_payload_root(runtime, skill_name)
    installed_entry = payload_root / "SKILL.md"
    result.checked_payloads += 1

    if not source_entry.is_file():
        result.findings.append(
            Finding("WARN", skill_name, runtime, f"missing source entry {entry}")
        )
        return

    source_text = read_text(source_entry)
    installed_text = read_text(installed_entry)

    if has_dangling_source_ref(source_text):
        result.findings.append(
            Finding("WARN", skill_name, runtime, f"source entry references {DANGLING_SOURCE_REFS[0]}")
        )

    if not installed_entry.is_file():
        result.findings.append(
            Finding("WARN", skill_name, runtime, "runtime payload missing SKILL.md")
        )
        return

    if has_dangling_source_ref(installed_text):
        result.findings.append(
            Finding("WARN", skill_name, runtime, f"installed payload references {DANGLING_SOURCE_REFS[0]}")
        )

    if installed_text != source_text:
        result.findings.append(
            Finding("WARN", skill_name, runtime, "installed SKILL.md differs from selected source entry; rerun setup")
        )

    for shared_dir in SHARED_DIRS:
        source_shared = skill_dir / shared_dir
        if source_shared.exists() and not (payload_root / shared_dir).exists():
            result.findings.append(
                Finding("WARN", skill_name, runtime, f"runtime payload missing {shared_dir}/")
            )


def audit(dot_agent: Path) -> AuditResult:
    skills_root = dot_agent / "skills"
    result = AuditResult()

    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_name = skill_dir.name
        manifest_path = skill_dir / "skill.toml"
        manifest = load_manifest(manifest_path) if manifest_path.is_file() else {}
        targets = manifest_targets(skill_dir, manifest)
        if not targets:
            continue

        result.checked_skills += 1
        contracts = manifest.get("runtime_contracts")
        if contracts:
            result.findings.append(
                Finding("INFO", skill_name, "source", "declares runtime_contracts; setup does not bundle named contracts yet")
            )

        for runtime in targets:
            if runtime not in {"claude", "codex"}:
                result.findings.append(
                    Finding("WARN", skill_name, runtime, "unknown runtime target")
                )
                continue
            audit_skill_runtime(
                result,
                skill_dir=skill_dir,
                skill_name=skill_name,
                runtime=runtime,
                entry=runtime_entry(runtime, manifest),
            )

    for runtime in ("claude", "codex"):
        directory_agent = runtime_home(runtime) / "skills" / "AGENTS.md"
        if directory_agent.exists():
            result.findings.append(
                Finding("WARN", "skills", runtime, "runtime skills directory contains AGENTS.md; directory policy should stay source-only")
            )

    return result


def as_dict(result: AuditResult) -> dict[str, Any]:
    return {
        "checked_skills": result.checked_skills,
        "checked_payloads": result.checked_payloads,
        "findings": [finding.__dict__ for finding in result.findings],
    }


def print_text(result: AuditResult) -> None:
    warning_count = sum(1 for finding in result.findings if finding.severity == "WARN")
    info_count = sum(1 for finding in result.findings if finding.severity == "INFO")
    print("Skill Instruction Audit")
    print(f"Checked {result.checked_skills} skills, {result.checked_payloads} runtime payloads.")
    if not result.findings:
        print("OK: no skill instruction drift found.")
        return
    if warning_count:
        print(f"WARN: {warning_count} issue(s) found.")
    if info_count:
        print(f"INFO: {info_count} note(s).")
    for finding in result.findings:
        print(f"{finding.severity}: {finding.skill} [{finding.runtime}] {finding.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit installed skill payloads for instruction drift.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when WARN findings exist.")
    args = parser.parse_args()

    result = audit(dot_agent_home())
    if args.format == "json":
        print(json.dumps(as_dict(result), indent=2, sort_keys=True))
    else:
        print_text(result)

    if args.strict and any(finding.severity == "WARN" for finding in result.findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
