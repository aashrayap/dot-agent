#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 on this machine.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        import toml_compat as tomllib


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    targets: list[str]
    default_entry: str
    claude_entry: str
    codex_entry: str
    composition: dict[str, list[str]]
    contract: dict[str, list[str]]
    implicit: bool
    explicit: list[str]


COMPOSITION_KEYS = (
    "parents",
    "children",
    "formats",
    "reads",
    "writes",
    "delegates",
    "handoffs",
)
CONTRACT_KEYS = (
    "inputs",
    "outputs",
    "scripts",
    "references",
    "assets",
    "state_reads",
    "state_writes",
    "tools",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a table")
    return data


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", "|"}:
            chunks: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                stripped = lines[index].strip()
                if stripped:
                    chunks.append(stripped)
                index += 1
            values[key] = " ".join(chunks)
            continue
        values[key] = value.strip('"').strip("'")
        index += 1
    return values


def string_list(table: dict[str, Any], key: str) -> list[str]:
    value = table.get(key, [])
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def load_skill(skill_dir: Path) -> Skill | None:
    manifest_path = skill_dir / "skill.toml"
    skill_md_path = skill_dir / "SKILL.md"
    if not manifest_path.is_file() or not skill_md_path.is_file():
        return None

    manifest = load_toml(manifest_path)
    meta = frontmatter(read_text(skill_md_path))
    composition_raw = manifest.get("composition", {})
    contract_raw = manifest.get("contract", {})
    invoke_raw = manifest.get("invoke", {})

    composition = {
        key: string_list(composition_raw, key) if isinstance(composition_raw, dict) else []
        for key in COMPOSITION_KEYS
    }
    contract = {
        key: string_list(contract_raw, key) if isinstance(contract_raw, dict) else []
        for key in CONTRACT_KEYS
    }

    return Skill(
        name=str(manifest.get("name", skill_dir.name)),
        description=meta.get("description", ""),
        targets=string_list(manifest, "targets"),
        default_entry=str(manifest.get("default_entry", "SKILL.md")),
        claude_entry=str(manifest.get("claude_entry", "")),
        codex_entry=str(manifest.get("codex_entry", "")),
        composition=composition,
        contract=contract,
        implicit=bool(invoke_raw.get("implicit", False)) if isinstance(invoke_raw, dict) else False,
        explicit=string_list(invoke_raw, "explicit") if isinstance(invoke_raw, dict) else [],
    )


def escape_cell(value: str) -> str:
    value = value.replace("\n", " ").replace("|", "\\|")
    return re.sub(r"\s+", " ", value).strip()


def short_text(value: str, *, limit: int = 150) -> str:
    value = escape_cell(value)
    if len(value) <= limit:
        return value
    cut = value.rfind(" ", 0, limit - 1)
    if cut < limit * 0.6:
        cut = limit - 1
    return value[:cut].rstrip() + "..."


def compact(values: list[str], *, limit: int = 3) -> str:
    if not values:
        return "-"
    visible = values[:limit]
    suffix = f", +{len(values) - limit}" if len(values) > limit else ""
    return escape_cell(", ".join(visible) + suffix)


def bullet_list(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{escape_cell(value)}`" for value in values)


def skill_link(skill: Skill) -> str:
    return f"[`{skill.name}`]({skill.name}/SKILL.md)"


def render_routing_table(skills: list[Skill]) -> list[str]:
    lines = [
        "## Routing Table",
        "",
        "| Skill | Use when | Targets | Explicit | Children | Handoffs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for skill in skills:
        lines.append(
            "| "
            + " | ".join(
                [
                    skill_link(skill),
                    short_text(skill.description) or "-",
                    compact(skill.targets),
                    compact(skill.explicit),
                    compact(skill.composition["children"]),
                    compact(skill.composition["handoffs"]),
                ]
            )
            + " |"
        )
    return lines


def render_state_table(skills: list[Skill]) -> list[str]:
    lines = [
        "## State Surfaces",
        "",
        "| Skill | Reads | Writes |",
        "| --- | --- | --- |",
    ]
    for skill in skills:
        reads = skill.contract["state_reads"] or skill.composition["reads"]
        writes = skill.contract["state_writes"] or skill.composition["writes"]
        lines.append(
            f"| {skill_link(skill)} | {compact(reads, limit=4)} | {compact(writes, limit=4)} |"
        )
    return lines


def render_edges(skills: list[Skill]) -> list[str]:
    edges: list[tuple[str, str, str]] = []
    for skill in skills:
        for parent in skill.composition["parents"]:
            edges.append((parent, skill.name, "parent"))
        for child in skill.composition["children"]:
            edges.append((skill.name, child, "child"))
        for format_ref in skill.composition["formats"]:
            edges.append((skill.name, format_ref, "uses format"))
        for delegate in skill.composition["delegates"]:
            edges.append((skill.name, delegate, "delegates"))
        for handoff in skill.composition["handoffs"]:
            edges.append((skill.name, handoff, "hands off"))

    lines = [
        "## Composition Edges",
        "",
        "| From | To | Relation |",
        "| --- | --- | --- |",
    ]
    for source, target, relation in sorted(set(edges), key=lambda item: (item[0], item[1], item[2])):
        lines.append(f"| `{escape_cell(source)}` | `{escape_cell(target)}` | {relation} |")
    return lines


def render_details(skills: list[Skill]) -> list[str]:
    lines = ["## Skill Details", ""]
    for skill in skills:
        lines.extend(
            [
                f"### {skill.name}",
                "",
                f"- Use when: {escape_cell(skill.description) or 'not declared'}",
                f"- Targets: {bullet_list(skill.targets)}",
                f"- Entry points: default `{skill.default_entry}`"
                + (f", Claude `{skill.claude_entry}`" if skill.claude_entry else "")
                + (f", Codex `{skill.codex_entry}`" if skill.codex_entry else ""),
                f"- Explicit invokes: {bullet_list(skill.explicit)}",
                f"- Implicit invoke: `{str(skill.implicit).lower()}`",
                f"- Parents: {bullet_list(skill.composition['parents'])}",
                f"- Children: {bullet_list(skill.composition['children'])}",
                f"- Uses format from: {bullet_list(skill.composition['formats'])}",
                f"- Reads: {bullet_list(skill.composition['reads'])}",
                f"- Writes: {bullet_list(skill.composition['writes'])}",
                f"- Delegates: {bullet_list(skill.composition['delegates'])}",
                f"- Handoffs: {bullet_list(skill.composition['handoffs'])}",
                f"- Inputs: {bullet_list(skill.contract['inputs'])}",
                f"- Outputs: {bullet_list(skill.contract['outputs'])}",
                f"- State reads: {bullet_list(skill.contract['state_reads'])}",
                f"- State writes: {bullet_list(skill.contract['state_writes'])}",
                f"- Tools: {bullet_list(skill.contract['tools'])}",
                f"- Read next: [`skills/{skill.name}/SKILL.md`]({skill.name}/SKILL.md)",
                "",
            ]
        )
    return lines


def render_index(skills: list[Skill]) -> str:
    lines = [
        "# Skill Index",
        "",
        "<!-- Generated by scripts/generate-skill-index.py. Do not edit directly. -->",
        "",
        "Agent routing index generated from `skills/*/skill.toml` and `SKILL.md` frontmatter.",
        "Consult this before choosing or composing skills, then read only the specific `SKILL.md` files needed.",
        "",
    ]
    for section in (
        render_routing_table(skills),
        render_state_table(skills),
        render_edges(skills),
        render_details(skills),
    ):
        lines.extend(section)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_index() -> str:
    root = repo_root()
    skills_root = root / "skills"
    skills = [
        skill
        for skill_dir in sorted(skills_root.iterdir(), key=lambda path: path.name)
        if skill_dir.is_dir()
        for skill in [load_skill(skill_dir)]
        if skill is not None
    ]
    skills.sort(key=lambda skill: skill.name)
    return render_index(skills)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate skills/SKILL_INDEX.md")
    parser.add_argument("--check", action="store_true", help="fail if the index is stale")
    args = parser.parse_args()

    root = repo_root()
    output_path = root / "skills" / "SKILL_INDEX.md"
    generated = build_index()

    if args.check:
        current = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        if current != generated:
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                generated.splitlines(keepends=True),
                fromfile=str(output_path),
                tofile="generated",
            )
            sys.stderr.write("ERROR: skills/SKILL_INDEX.md is stale. Run scripts/generate-skill-index.py.\n")
            sys.stderr.writelines(diff)
            return 1
        print("Skill index is current.")
        return 0

    output_path.write_text(generated, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
