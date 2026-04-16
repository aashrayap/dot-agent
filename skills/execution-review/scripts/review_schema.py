#!/usr/bin/env python3
from __future__ import annotations

import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - py310 fallback
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:  # pragma: no cover - optional fallback
        tomllib = None  # type: ignore[assignment]

DOT_AGENT_HOME = Path(os.environ.get("DOT_AGENT_HOME", Path.home() / ".dot-agent"))
STATE_ROOT = DOT_AGENT_HOME / "state" / "collab" / "execution-reviews"
REPORTS_DIR = STATE_ROOT / "reports"
DB_PATH = STATE_ROOT / "reviews.sqlite"
HISTORY_PATH = STATE_ROOT / "history.jsonl"
HERMES_FINDINGS_PATH = STATE_ROOT / "hermes-findings.jsonl"
CONFIG_PATH = STATE_ROOT / "config.toml"

READ_PATTERNS = (
    "ls ",
    "find ",
    "rg ",
    "sed ",
    "cat ",
    "head ",
    "tail ",
    "wc ",
    "git status",
    "git diff",
    "git log",
    "git show",
    "sqlite3 ",
    "jq ",
)

VERIFY_PATTERNS = (
    "pytest",
    "py.test",
    "ruff",
    "mypy",
    "tox",
    "npx vitest",
    "vitest",
    "jest",
    "playwright",
    "npm test",
    "pnpm test",
    "yarn test",
    "npm run lint",
    "pnpm lint",
    "yarn lint",
    "go test",
    "cargo test",
    "cargo clippy",
    "bundle exec rspec",
    "rspec",
    "phpunit",
    "swift test",
    "xcodebuild test",
    "gradlew test",
    "mix test",
    "deno test",
    "tsc ",
    "eslint",
    "make test",
    "make lint",
    "check ",
    "lint ",
)

FEEDBACK_PATTERNS: dict[str, tuple[str, ...]] = {
    "length": ("concise", "shorter", "too long", "brief", "ultra concise", "tldr"),
    "format": ("bullet", "bullets", "table", "prose", "paragraph", "markdown"),
    "retry": ("redo", "rewrite", "rephrase", "again", "not this", "try again"),
}


def ensure_state_layout() -> None:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_window(spec: str) -> float:
    raw = spec.strip().lower()
    if raw in {"day", "daily"}:
        return 24.0
    if raw in {"week", "weekly"}:
        return 24.0 * 7
    if raw.endswith("h"):
        return float(raw[:-1])
    if raw.endswith("d"):
        return float(raw[:-1]) * 24.0
    if raw.endswith("w"):
        return float(raw[:-1]) * 24.0 * 7
    return float(raw)


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def window_bounds(window_hours: float) -> tuple[datetime, datetime]:
    end = utc_now()
    return end - timedelta(hours=window_hours), end


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def excerpt(text: str | None, limit: int = 220) -> str:
    value = normalize_ws(text or "")
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def to_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def format_seconds(seconds: float | int | None) -> str:
    total = int(round(seconds or 0))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def classify_command_text(command: str) -> dict[str, bool]:
    normalized = normalize_ws(command).lower()
    return {
        "read": any(normalized.startswith(pattern) for pattern in READ_PATTERNS),
        "verify": any(pattern in normalized for pattern in VERIFY_PATTERNS),
    }


def detect_feedback_signals(messages: list[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for raw in messages:
        lowered = normalize_ws(raw).lower()
        if not lowered:
            continue
        for label, patterns in FEEDBACK_PATTERNS.items():
            if any(pattern in lowered for pattern in patterns):
                counts[label] += 1
    return dict(counts)


def load_identity_rules() -> list[dict[str, str]]:
    if tomllib is None or not CONFIG_PATH.exists():
        return []
    try:
        data = tomllib.loads(CONFIG_PATH.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return []
    mappings = data.get("identity") or data.get("identities") or []
    if not isinstance(mappings, list):
        return []
    rules: list[dict[str, str]] = []
    for item in mappings:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        prefix = str(item.get("path_prefix", "")).strip()
        if name and prefix:
            rules.append({"name": name, "path_prefix": prefix})
    rules.sort(key=lambda item: len(item["path_prefix"]), reverse=True)
    return rules


def resolve_identity(cwd: str | None) -> str:
    if not cwd:
        return "default"
    for rule in load_identity_rules():
        if cwd.startswith(rule["path_prefix"]):
            return rule["name"]
    return "default"


def build_response_fit(
    *,
    first_user_message: str,
    final_response_excerpt: str,
    user_messages: list[str],
    assistant_messages: int,
    commentary_messages: int,
    final_messages: int,
) -> dict[str, Any]:
    followups = user_messages[1:] if len(user_messages) > 1 else []
    return {
        "first_request": excerpt(first_user_message, 280),
        "final_response_excerpt": excerpt(final_response_excerpt, 420),
        "followup_user_messages": len(followups),
        "feedback_signals": detect_feedback_signals(followups),
        "assistant_messages": assistant_messages,
        "commentary_messages": commentary_messages,
        "final_messages": final_messages,
    }


def aggregate_normalized_sessions(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "summary": {
                "sessions": 0,
                "unique_cwds": 0,
                "wall_seconds": 0,
                "wall_human": "0s",
                "context_switches": 0,
                "edits": 0,
                "verifications": 0,
                "exec_failures": 0,
                "subagent_count": 0,
            },
            "by_runtime": [],
            "by_day": [],
            "by_cwd": [],
            "sessions": [],
        }

    ordered = sorted(records, key=lambda item: item.get("started_at") or "")
    summary = {
        "sessions": len(ordered),
        "unique_cwds": len({item.get("cwd") for item in ordered if item.get("cwd")}),
        "wall_seconds": sum(int(item.get("wall_seconds") or 0) for item in ordered),
        "edits": sum(int(item.get("edits") or 0) for item in ordered),
        "verifications": sum(int(item.get("verifications") or 0) for item in ordered),
        "exec_failures": sum(int(item.get("exec_failures") or 0) for item in ordered),
        "subagent_count": sum(int(item.get("subagent_count") or 0) for item in ordered),
        "context_switches": 0,
    }
    summary["wall_human"] = format_seconds(summary["wall_seconds"])

    by_runtime: dict[str, dict[str, Any]] = {}
    by_day: dict[str, dict[str, Any]] = {}
    by_cwd: dict[str, dict[str, Any]] = {}

    previous_cwd = None
    for item in ordered:
        cwd = item.get("cwd")
        if previous_cwd is not None and cwd and cwd != previous_cwd:
            summary["context_switches"] += 1
        previous_cwd = cwd or previous_cwd

        runtime = item.get("runtime") or "unknown"
        runtime_entry = by_runtime.setdefault(
            runtime,
            {
                "runtime": runtime,
                "sessions": 0,
                "wall_seconds": 0,
                "wall_human": "0s",
                "edits": 0,
                "verifications": 0,
                "exec_failures": 0,
            },
        )
        runtime_entry["sessions"] += 1
        runtime_entry["wall_seconds"] += int(item.get("wall_seconds") or 0)
        runtime_entry["edits"] += int(item.get("edits") or 0)
        runtime_entry["verifications"] += int(item.get("verifications") or 0)
        runtime_entry["exec_failures"] += int(item.get("exec_failures") or 0)

        started_day = None
        if item.get("started_at"):
            started = to_dt(item["started_at"])
            if started:
                started_day = started.astimezone().date().isoformat()
        started_day = started_day or "unknown"
        day_entry = by_day.setdefault(
            started_day,
            {
                "day": started_day,
                "sessions": 0,
                "wall_seconds": 0,
                "wall_human": "0s",
                "edits": 0,
                "verifications": 0,
                "exec_failures": 0,
                "runtimes": Counter(),
                "unique_cwds": set(),
            },
        )
        day_entry["sessions"] += 1
        day_entry["wall_seconds"] += int(item.get("wall_seconds") or 0)
        day_entry["edits"] += int(item.get("edits") or 0)
        day_entry["verifications"] += int(item.get("verifications") or 0)
        day_entry["exec_failures"] += int(item.get("exec_failures") or 0)
        day_entry["runtimes"][runtime] += 1
        if cwd:
            day_entry["unique_cwds"].add(cwd)

        if cwd:
            cwd_entry = by_cwd.setdefault(
                cwd,
                {
                    "cwd": cwd,
                    "sessions": 0,
                    "wall_seconds": 0,
                    "wall_human": "0s",
                    "edits": 0,
                    "verifications": 0,
                    "exec_failures": 0,
                    "runtimes": Counter(),
                },
            )
            cwd_entry["sessions"] += 1
            cwd_entry["wall_seconds"] += int(item.get("wall_seconds") or 0)
            cwd_entry["edits"] += int(item.get("edits") or 0)
            cwd_entry["verifications"] += int(item.get("verifications") or 0)
            cwd_entry["exec_failures"] += int(item.get("exec_failures") or 0)
            cwd_entry["runtimes"][runtime] += 1

    runtime_rows = []
    for runtime in sorted(by_runtime):
        row = by_runtime[runtime]
        row["wall_human"] = format_seconds(row["wall_seconds"])
        runtime_rows.append(row)

    day_rows = []
    for day in sorted(by_day):
        row = by_day[day]
        row["wall_human"] = format_seconds(row["wall_seconds"])
        row["runtimes"] = dict(row["runtimes"])
        row["unique_cwds"] = len(row["unique_cwds"])
        day_rows.append(row)

    cwd_rows = []
    for cwd in sorted(by_cwd, key=lambda key: (-by_cwd[key]["wall_seconds"], key)):
        row = by_cwd[cwd]
        row["wall_human"] = format_seconds(row["wall_seconds"])
        row["runtimes"] = dict(row["runtimes"])
        cwd_rows.append(row)

    return {
        "summary": summary,
        "by_runtime": runtime_rows,
        "by_day": day_rows,
        "by_cwd": cwd_rows,
        "sessions": ordered,
    }
