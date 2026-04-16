---
name: execution-review
description: Evidence-first review of recent local Codex and Claude Code sessions, entered from Claude Code.
---

# Execution Review

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
- keep Hermes findings clearly separate when present
