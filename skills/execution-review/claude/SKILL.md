---
name: execution-review
description: Evidence-first review of recent local Codex and Claude Code sessions, entered from Claude Code.
---

# Execution Review

## Composes With

- Parent: day-end or weekly review request.
- Children: `focus`/roadmap helpers and `projects` helpers for confirmed state changes.
- Uses format from: none.
- Reads state from: Codex/Claude session logs, `roadmap.md`, active projects, execution memory, PR signals, and optional Hermes findings.
- Writes through: `skills/focus/scripts/roadmap.py`, `projects` helpers, and execution-review report/history files.
- Hands off to: `focus` for roadmap cleanup and `projects` for durable closure updates.
- Receives back from: `spec-new-feature` and `projects` through execution memory and PR refs.

Use the shared execution-review workflow from Claude Code.

## Runtime Note

- You are running from Claude Code, but the scripts can review `claude`, `codex`, or `all` local runtime artifacts.
- Prefer `--runtime all` unless the user clearly wants a Claude-only pass.

## Quick Start

1. `scripts/execution-review-setup.py [window]`
2. `scripts/fetch-execution-sessions.py --runtime all --window <window>`
3. `scripts/inspect-execution-session.py --runtime <runtime> --session-id <id>`
4. `scripts/render-execution-review.py --runtime all --window <window> [--save] [--record]`

Then follow the shared evidence-first review contract:
- inspect only the sessions that matter
- score response fit, skill leverage, verification, focus, grounding, and efficiency
- for daily review requests, run the shared Daily Closure Loop and project ribbon rules
- keep full session ids in every citation; add turn indices when the inspected payload exposes them
- keep Hermes findings clearly separate when present
