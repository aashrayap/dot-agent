---
name: execution-review
description: Review recent Codex and Claude Code sessions to diagnose response fit, skill usage, workflow efficiency, verification discipline, and recurring failures from local runtime artifacts.
---

# Execution Review

Use this when the user wants a daily review, weekly review, workflow diagnosis, response-style analysis, skill-usage analysis, or a structured retrospective across recent local agent sessions.

## Quick Start

1. Run `scripts/execution-review-setup.py [window]` first.
2. Run `scripts/fetch-execution-sessions.py --runtime <all|codex|claude> --window <window>`.
3. Inspect only the sessions that matter with `scripts/inspect-execution-session.py --runtime <runtime> --session-id <id>`.
4. Render the actual review with `scripts/render-execution-review.py --runtime <all|codex|claude> --window <window> [--save] [--record]`.

`window` accepts `day`, `week`, raw hours like `24`, or suffixed values like `36h`, `7d`.

## Intent

The review system is evidence-first:

- runtime adapters read local artifacts from Codex and Claude Code
- normalized evidence is stored under `~/.dot-agent/state/collab/execution-reviews/`
- the review layer scores and interprets that evidence
- Hermes findings are optional additive inputs, not the source of truth for raw telemetry
- the strategic/tactical/disposable lens should inform whether time is going to durable domain advantage, useful workflow acceleration, or disposable runtime/tool churn

## Daily Review Workflow

1. Run setup.
2. Run `scripts/fetch-execution-sessions.py --runtime all --window <window>`.
3. From the payload, identify:
   - top sessions by wall time
   - sessions with `edits > 0` and `verifications == 0`
   - sessions with `exec_failures > 0`
   - sessions with response-fit feedback signals
   - one session that looks especially strong
4. Inspect that small set with `scripts/inspect-execution-session.py`.
5. Cluster sessions into workstreams.
6. Produce the report.

## Weekly Review Workflow

1. Run setup.
2. Run `scripts/fetch-execution-sessions.py --runtime all --window week`.
3. Use the aggregates to spot:
   - heavy context-switch days
   - good vs weak verification coverage
   - repeated failure modes
   - response-fit drift
   - skill-usage patterns and missed opportunities
4. Inspect representative sessions.
5. Produce the weekly review and 1-3 process experiments.

## Scorecard

Judge only after inspecting evidence.

Use this rubric:

| Dimension | What to look for |
| --- | --- |
| Focus | Low avoidable fragmentation, coherent workstreams, limited unnecessary cwd switching |
| Grounding | Real inspection before changes or strong conclusions |
| Verification | Tests, lint, checks, or other explicit validation after meaningful edits |
| Response Fit | Whether the response shape matched the ask, based on excerpts and user follow-up/correction signals |
| Skill Leverage | Whether existing skills/patterns were used well or skipped when they would have helped |
| Workflow Efficiency | Time/tokens/actions relative to actual progress, without over-scoring shallow churn |

Track recurring failures separately even when they are not a scored dimension.

Also report strategic/tactical/disposable allocation:

- Strategic: domain expertise, proprietary context/data, judgment, evals, decision loops, trust.
- Tactical: harnesses, skills, workflows, reviews, deterministic helpers that accelerate strategic work.
- Disposable: tool-specific tricks likely to be replaced by upstream runtime/model releases.

## Guardrails

- Prefer a small number of inspected sessions over opening everything.
- Treat `cwd` as a hint, not perfect ground truth.
- A no-edit research session is not automatically poor if it reduced uncertainty decisively.
- A session with edits and no verification is a real risk.
- Hermes findings should be clearly labeled as secondary interpretation when present.

## Persistence

- Normalized evidence lives in `~/.dot-agent/state/collab/execution-reviews/reviews.sqlite`
- Append-only review history lives in `~/.dot-agent/state/collab/execution-reviews/history.jsonl`
- Saved markdown reports live in `~/.dot-agent/state/collab/execution-reviews/reports/`
- Optional Hermes findings can be read from `~/.dot-agent/state/collab/execution-reviews/hermes-findings.jsonl`

## Hermes Consumer Contract

Hermes findings are additive, not authoritative over raw telemetry.

To append Hermes-side findings into the shared state:

`scripts/write-hermes-findings.py --window <window> --runtime <runtime|all> --title <title> --finding <text> --recommendation <text>`

Then rerun `scripts/render-execution-review.py` for the matching window/runtime to merge those findings into the final markdown review.
