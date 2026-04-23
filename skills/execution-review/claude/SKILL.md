---
name: execution-review
description: Evidence-first review of recent local Codex and Claude Code sessions, entered from Claude Code.
---

# Execution Review

## Composes With

- Parent: forensic execution review, workflow diagnosis, session-review, or weekly retrospective request.
- Children: runtime evidence scripts, optional Hermes findings, and `excalidraw-diagram` when a forensic review needs a durable workflow or session-shape visual.
- Uses format from: `excalidraw-diagram` for human-facing session pipeline, workflow, or before/after visuals when useful.
- Reads state from: Codex/Claude session logs, execution-review evidence/history, PR signals, roadmap rows when relevant, and optional Hermes findings.
- Writes through: execution-review report/history files only.
- Hands off to: `daily-review` for human day-end closure, recap, and roadmap drainage; `spec-new-feature`, `focus`, or `review` only as recommended follow-up surfaces.
- Receives back from: `spec-new-feature`, `focus`, `review`, PR refs, and prior execution-review reports as evidence.

Use the shared execution-review workflow from Claude Code.

## Runtime Note

- You are running from Claude Code, but the scripts can review `claude`, `codex`, or `all` local runtime artifacts.
- Prefer `--runtime all` unless the user clearly wants a Claude-only pass.

## Quick Start

1. `scripts/execution-review-setup.py [window]`
2. `scripts/fetch-execution-sessions.py --runtime all --window <window>`
3. `scripts/inspect-execution-session.py --runtime <runtime> --session-id <id>`
4. `scripts/render-execution-review.py --runtime all --window <window> [--save] [--record]`

For the always-on Hermes workflow check, run `scripts/hermes-daily.py --write`.
It writes the human review synthesis to
`~/.dot-agent/state/collab/hermes/daily/YYYY-MM-DD.md`; background heartbeats
should summarize review-worthy findings in the thread inbox.

Then follow the shared evidence-first review contract:
- inspect only the sessions that matter
- score response fit, skill leverage, verification, focus, grounding, and efficiency
- for transcript reviews, apply the shared typed pipeline: intake, orient, plan/announce, act, verify, synthesize, handoff
- for day-end closure requests, hand off human closure, recap, and roadmap drainage to `daily-review`
- keep full session ids in every citation; add turn indices when the inspected payload exposes them
- keep Hermes findings clearly separate when present
- use or link an Excalidraw diagram for non-trivial workflow/session-shape explanations; keep exact scores and citations in text
- flag artifact contract drift when a final answer exposes editable/source artifacts instead of the requested human-readable deliverable
