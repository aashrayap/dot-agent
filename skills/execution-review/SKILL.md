---
name: execution-review
description: Review recent Codex and Claude Code sessions to diagnose response fit, skill usage, workflow efficiency, verification discipline, and recurring failures from local runtime artifacts.
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

Use this when the user wants a daily review, weekly review, workflow diagnosis, response-style analysis, skill-usage analysis, or a structured retrospective across recent local agent sessions.

## Quick Start

1. Run `scripts/execution-review-setup.py [window]` first.
2. Run `scripts/fetch-execution-sessions.py --runtime <all|codex|claude> --window <window>`.
3. Inspect only the sessions that matter with `scripts/inspect-execution-session.py --runtime <runtime> --session-id <id>`.
4. Render the actual review with `scripts/render-execution-review.py --runtime <all|codex|claude> --window <window> [--save] [--record]`.
5. For day-end reviews, run the Daily Closure Loop below before final recommendations.

`window` accepts `day`, `week`, raw hours like `24`, or suffixed values like `36h`, `7d`.

## Intent

The review system is evidence-first:

- runtime adapters read local artifacts from Codex and Claude Code
- normalized evidence is stored under `~/.dot-agent/state/collab/execution-reviews/`
- the review layer scores and interprets that evidence
- daily mode reconstructs what happened, reconciles closure signals, and writes a recap
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
5. Cluster sessions into logical workstreams. Treat `cwd` as a hint only: one repo can hold multiple projects, and one project can span repos or runtimes.
6. Build a chronological project ribbon before scoring. It should answer, at a glance, how the day was actually spent.
7. Run the Daily Closure Loop.
8. Produce the report with citations, scorecard, closure state, and 1-3 concrete workflow changes.

## Daily Closure Loop

Use this when the user asks for a daily review, day-end review, recap, or closure pass.

1. Establish the local day boundary for the user's timezone.
2. Read the active roadmap context and project execution contexts with the existing helper scripts.
3. Gather external closure signals when available:
   - merged PRs authored by the user since local day start via `gh search prs --author=@me --state=merged --merged=">=<ISO>"`
   - Linear or issue-tracker closures only when a configured connector/tool is available
   - explicit completion markers already present in `roadmap.md`, `projects/*/project.md`, or `execution.md`
4. Reconcile closures:
   - PR merged for a known project/session/ref: treat as an authoritative completion signal.
   - Tracker item closed without a PR or project ref: surface as a discrepancy for user confirmation.
   - Chat activity without a closure signal: leave as in-progress unless the user confirms completion.
   - Off-plan PRs or tracker closures: include in the recap, but do not invent project state.
5. Present the reconstruction before mutating durable state:
   - completed work grouped by logical project
   - discrepancies that need user confirmation
   - off-plan activity
   - sessions that look in-progress, abandoned, or blocked
6. If the user confirms closure updates, route writes through the owning surface:
   - project session completion goes through `projects` helpers, especially `complete-session.py`
   - execution memory updates go through `update-execution.py` when the state change is known
   - roadmap cleanup goes through the `focus` skill or its helper scripts
7. Save the final recap with `--save --record` when the user wants durable history.

Daily review is allowed to recommend state changes without applying them. It should only write project/focus state after the user confirms ambiguous closures.

## Project Ribbon

The report should include a chronological ribbon for daily mode:

```markdown
| # | Time | Wall | Project | Runtime(s) | cwd(s) | Sessions |
|---|------|------|---------|------------|--------|----------|
```

Rules:

- Project names are logical workstreams, not repo names.
- Use project slugs from `~/.dot-agent/state/projects/` when a session maps cleanly.
- Otherwise infer a short workstream label from the request and cwd, and mark it as inferred.
- Keep every session id complete and untruncated.
- If an inspected session exposes turn-level detail, cite findings as `<full-session-id>:turn-<n>`.
- If turn indices are unavailable, cite `<full-session-id>` and say turn-level detail was not exposed by the adapter.

## Weekly Review Workflow

1. Run setup.
2. Run `scripts/fetch-execution-sessions.py --runtime all --window week`.
3. Use the aggregates to spot:
   - heavy context-switch days
   - good vs weak verification coverage
   - repeated failure modes
   - response-fit drift
   - skill-usage patterns and missed opportunities
   - project effort, compression, and precision metrics when `projects/execution.md` provides them
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
- Do not equate repos with projects.
- A no-edit research session is not automatically poor if it reduced uncertainty decisively.
- A session with edits and no verification is a real risk.
- Hermes findings should be clearly labeled as secondary interpretation when present.
- Every recommendation should be grounded in an inspected session, closure discrepancy, or recurring metric. Avoid generic workflow advice.
- Do not port Claude-specific command protocols, allowed-tool constraints, or ROADMAP.md behavior into this shared skill.

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
