#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        import toml_compat as tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


RESPONSE_CONTRACT_ANCHOR = "Human Response Contract"
SESSION_FOCUS_ANCHOR = "This Session Focus"
RUNTIME_PREFERENCE_ANCHOR = "Codex is Ash's strongly preferred runtime"


@dataclass
class RepoSource:
    path: Path
    reason: str


@dataclass
class RepoFinding:
    severity: str
    repo: str
    message: str


@dataclass
class RepoStatus:
    repo: str
    sources: list[str]
    agents: str
    claude: str
    findings: list[RepoFinding] = field(default_factory=list)


@dataclass
class AuditResult:
    discovered_paths: int = 0
    checked_repos: list[RepoStatus] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def findings(self) -> list[RepoFinding]:
        return [finding for repo in self.checked_repos for finding in repo.findings]


def dot_agent_home() -> Path:
    return Path(os.environ.get("DOT_AGENT_HOME", Path(__file__).resolve().parents[1])).expanduser()


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def pathish(value: str) -> bool:
    return value.startswith("/") or value.startswith("~/")


def iter_path_strings(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        if pathish(node):
            yield node
        return
    if isinstance(node, list):
        for item in node:
            yield from iter_path_strings(item)
        return
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and pathish(key):
                yield key
            yield from iter_path_strings(value)


def codex_project_paths(config_path: Path) -> list[RepoSource]:
    data = load_toml(config_path)
    projects = data.get("projects")
    sources: list[RepoSource] = []
    if isinstance(projects, dict):
        for key in projects:
            if isinstance(key, str) and pathish(key):
                sources.append(RepoSource(Path(key).expanduser(), f"codex config {config_path}"))
    return sources


def allowlist_paths(path: Path) -> list[RepoSource]:
    if not path.is_file():
        return []
    data = load_toml(path)
    return [RepoSource(Path(raw).expanduser(), f"allowlist {path}") for raw in iter_path_strings(data)]


def latest_codex_state_db(home: Path) -> Path | None:
    candidates = sorted(home.glob("state_*.sqlite"), key=lambda item: item.stat().st_mtime)
    return candidates[-1] if candidates else None


def recent_codex_cwds(home: Path, *, days: int, limit: int) -> list[RepoSource]:
    db = latest_codex_state_db(home)
    if db is None:
        return []

    cutoff = int(time.time() - days * 86400)
    uri = f"file:{db}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.Error:
        return []

    try:
        rows = conn.execute(
            """
            SELECT cwd, MAX(updated_at) AS last_seen
            FROM threads
            WHERE cwd IS NOT NULL
              AND cwd != ''
              AND updated_at >= ?
            GROUP BY cwd
            ORDER BY last_seen DESC
            LIMIT ?
            """,
            (cutoff, limit),
        ).fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        conn.close()

    return [RepoSource(Path(row[0]).expanduser(), f"recent codex cwd {db}") for row in rows]


def git_root(path: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    root = completed.stdout.strip()
    return Path(root).resolve() if root else None


def should_skip(path: Path) -> bool:
    text = str(path)
    if text.startswith("/tmp/") or text.startswith("/private/tmp/"):
        return True
    if "/state/backups/" in text:
        return True
    return False


def normalize_repo(source: RepoSource) -> Path | None:
    path = source.path
    candidate = path.expanduser()
    try:
        candidate = candidate.resolve()
    except OSError:
        return None
    if not candidate.exists() or should_skip(candidate):
        return None
    if candidate.is_file():
        candidate = candidate.parent
    root = git_root(candidate)
    if root is None and source.reason.startswith("recent codex cwd"):
        return None
    return root or candidate


def discover_sources(dot_agent: Path, *, days: int, limit: int) -> list[RepoSource]:
    sources = [RepoSource(dot_agent, "dot-agent")]
    sources.extend(codex_project_paths(dot_agent / "codex" / "config.toml"))
    sources.extend(codex_project_paths(codex_home() / "config.toml"))
    sources.extend(allowlist_paths(dot_agent / "state" / "collab" / "active-repos.toml"))
    sources.extend(recent_codex_cwds(codex_home(), days=days, limit=limit))
    return sources


def file_status(path: Path) -> tuple[str, list[str]]:
    if not path.is_file():
        return "missing", []

    text = read_text(path)
    missing: list[str] = []
    if RESPONSE_CONTRACT_ANCHOR not in text:
        missing.append("response-contract")
    if SESSION_FOCUS_ANCHOR not in text:
        missing.append("session-focus")
    if RUNTIME_PREFERENCE_ANCHOR not in text:
        missing.append("runtime-preference")
    if missing:
        return "missing " + ",".join(missing), missing
    return "ok", []


def inspect_repo(repo: Path, sources: list[str]) -> RepoStatus:
    agents_status, agents_missing = file_status(repo / "AGENTS.md")
    claude_status, claude_missing = file_status(repo / "CLAUDE.md")
    status = RepoStatus(
        repo=str(repo),
        sources=sorted(set(sources)),
        agents=agents_status,
        claude=claude_status,
    )

    if agents_status == "missing" and claude_status == "missing":
        status.findings.append(
            RepoFinding("WARN", str(repo), "missing AGENTS.md and CLAUDE.md local instruction files")
        )
        return status

    if agents_status == "missing":
        status.findings.append(
            RepoFinding("WARN", str(repo), "missing AGENTS.md for Codex-local repo authority")
        )
    elif agents_missing:
        status.findings.append(
            RepoFinding("WARN", str(repo), f"AGENTS.md missing {', '.join(agents_missing)}")
        )

    if (repo / "CLAUDE.md").exists() and claude_missing:
        status.findings.append(
            RepoFinding("WARN", str(repo), f"CLAUDE.md missing {', '.join(claude_missing)}")
        )

    if agents_missing != claude_missing and (repo / "AGENTS.md").exists() and (repo / "CLAUDE.md").exists():
        status.findings.append(
            RepoFinding("WARN", str(repo), "AGENTS.md and CLAUDE.md have different shared fragment coverage")
        )

    return status


def audit(days: int, limit: int) -> AuditResult:
    dot_agent = dot_agent_home()
    sources = discover_sources(dot_agent, days=days, limit=limit)
    result = AuditResult(discovered_paths=len(sources))
    repos: dict[Path, list[str]] = {}

    for source in sources:
        repo = normalize_repo(source)
        if repo is None:
            result.skipped.append(f"{source.path} ({source.reason})")
            continue
        repos.setdefault(repo, []).append(source.reason)

    for repo, repo_sources in sorted(repos.items(), key=lambda item: str(item[0])):
        result.checked_repos.append(inspect_repo(repo, repo_sources))

    return result


def as_dict(result: AuditResult) -> dict[str, Any]:
    return {
        "discovered_paths": result.discovered_paths,
        "checked_repos": [
            {
                "repo": repo.repo,
                "sources": repo.sources,
                "agents": repo.agents,
                "claude": repo.claude,
                "findings": [finding.__dict__ for finding in repo.findings],
            }
            for repo in result.checked_repos
        ],
        "skipped": result.skipped,
    }


def print_text(result: AuditResult, *, show_ok: bool) -> None:
    findings = result.findings
    print("Repo Instruction Audit")
    print(f"Checked {len(result.checked_repos)} repo roots from {result.discovered_paths} discovered path(s).")
    if not findings:
        print("OK: no repo instruction drift found.")
    else:
        print(f"WARN: {len(findings)} issue(s) found.")
        for finding in findings:
            print(f"{finding.severity}: {finding.repo} | {finding.message}")

    if show_ok:
        for repo in result.checked_repos:
            print(f"STATUS: {repo.repo} | AGENTS={repo.agents} | CLAUDE={repo.claude}")
    if result.skipped:
        print(f"INFO: skipped {len(result.skipped)} non-existent or out-of-scope path(s).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit active repo AGENTS.md and CLAUDE.md drift.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--recent-days", type=int, default=30)
    parser.add_argument("--recent-limit", type=int, default=80)
    parser.add_argument("--show-ok", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when WARN findings exist.")
    args = parser.parse_args()

    result = audit(days=args.recent_days, limit=args.recent_limit)
    if args.format == "json":
        print(json.dumps(as_dict(result), indent=2, sort_keys=True))
    else:
        print_text(result, show_ok=args.show_ok)

    if args.strict and result.findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
