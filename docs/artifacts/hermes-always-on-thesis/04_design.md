---
status: approved
feature: hermes-always-on-thesis
---

# Design: hermes-always-on-thesis

## Chosen Direction

Use the minimal daily Hermes file contract.

Hermes remains an advisory layer on top of existing execution-review evidence. A new daily producer will:

- fetch recent Codex/Claude evidence
- scope it to `dot-agent` and `semi-stocks-2`, including descendant working directories
- compare workflow activity against a central thesis
- append one local machine-readable daily intake entry
- rewrite one curated daily synthesis for human review
- append compatibility findings to the existing `hermes-findings.jsonl` only when a review-worthy gate or loop signal exists

Human review timing:

- immediate: each producer run writes `state/collab/hermes/daily/YYYY-MM-DD.md`
- background: the heartbeat run should inspect that synthesis and surface review-worthy findings in the thread inbox
- morning: `morning-sync` sees compatibility findings through the existing tiny Hermes status line
- deep review: `execution-review` renders full Hermes findings for the matching window/runtime

## Relevant Principles

- Keep roadmap/focus mutation behind `focus`.
- Keep day-end closure behind `daily-review`.
- Keep raw/normalized telemetry under `execution-review`.
- Keep Hermes advisory and local-file-first.
- Keep human-facing output free of raw session ids and transcript internals.
- Put daily Hermes state under gitignored `state/`, not tracked docs.

## Decisions

### D1. Daily State Layout

Create local state under `state/collab/hermes/`:

- `thesis.md`: central operating thesis
- `daily/YYYY-MM-DD-log.jsonl`: append-only intake run log
- `daily/YYYY-MM-DD.md`: curated synthesis and human review surface

### D2. Scope Filter

The producer fetches runtime sessions for a window, then filters by cwd descendant relationship against:

- `/Users/ash/.dot-agent`
- `/Users/ash/Documents/2026/semi-stocks-2`

This avoids the current exact-cwd limitation and covers work in nested repo paths.

### D3. Loop Signals

First slice detects simple non-forward-progress signals:

- high-churn low-progress sessions
- repeated topic labels
- edit sessions without verification
- execution failures
- high context switching inside the scoped window

These are intentionally conservative and explainable.

### D4. Compatibility Findings

The producer writes to `execution-reviews/hermes-findings.jsonl` only for review-worthy findings. It uses deterministic IDs per date/finding kind to avoid duplicate findings across repeated background runs.

### D5. Human Review Surface

The curated synthesis is the canonical review surface. Background runs and morning sync should point humans there or summarize it, while raw intake remains local and append-only.

### D6. Background Trigger

Use an app heartbeat after implementation. The repo implementation remains an idempotent script, so scheduling can change without changing the file contract.

## Open Risks

- Topic-label repetition is a rough proxy for loop detection.
- The first slice does not inspect full transcripts, so it may miss semantic loops.
- Claude filtering is post-fetch, not source-filtered.
- Heartbeat scheduling lives in the app, not tracked repo state.
- Existing dirty worktree contains unrelated changes; execution must keep edits scoped.

## File Map

- `skills/execution-review/scripts/hermes-daily.py`: new daily producer.
- `skills/execution-review/SKILL.md`: shared contract update.
- `skills/execution-review/codex/SKILL.md`: Codex wrapper quick-start update.
- `skills/execution-review/claude/SKILL.md`: Claude wrapper quick-start update.
- `docs/artifacts/hermes-always-on-thesis/05_tasks.md`: execution task receipt.
- `state/collab/hermes/`: local generated runtime output, gitignored.
