---
name: execution-review
description: Review recent Codex and Claude Code sessions to diagnose response fit, skill usage, workflow efficiency, verification discipline, and recurring failures from local runtime artifacts.
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

Use this when the user wants forensic review of agent sessions, workflow diagnosis, response-style analysis, skill-usage analysis, verification analysis, or a structured retrospective across recent local agent sessions.

Do not use this skill as the human daily closure surface. If the user wants day-end recap, completed-row drainage, or roadmap cleanup, hand off to the future/new `daily-review` surface and keep any execution-review output limited to forensic evidence and recommendations.

For non-trivial reviews, especially those comparing session quality, workflow
shape, or before/after process changes, lead with or link to an Excalidraw
diagram. Keep exact scores, citations, and findings in text.

## Quick Start

1. Run `scripts/execution-review-setup.py [window]` first.
2. Run `scripts/fetch-execution-sessions.py --runtime <all|codex|claude> --window <window>`.
3. Inspect only the sessions that matter with `scripts/inspect-execution-session.py --runtime <runtime> --session-id <id>`.
4. Render the actual review with `scripts/render-execution-review.py --runtime <all|codex|claude> --window <window> [--save] [--record]`.
5. For day-end closure requests, do not drain roadmap state here; hand off closure work to `daily-review`.

`window` accepts `day`, `week`, raw hours like `24`, or suffixed values like `36h`, `7d`.

## Intent

The review system is evidence-first:

- runtime adapters read local artifacts from Codex and Claude Code
- normalized evidence is stored under `~/.dot-agent/state/collab/execution-reviews/`
- the review layer scores and interprets that evidence
- windowed mode reconstructs what happened, evaluates agent quality, and identifies risks or follow-up recommendations
- Hermes findings are optional additive inputs, not the source of truth for raw telemetry
- the strategic/tactical/disposable lens should inform whether time is going to durable domain advantage, useful workflow acceleration, or disposable runtime/tool churn

## Forensic Review Workflow

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
6. Build a chronological workstream ribbon before scoring. It should answer, at a glance, how agent effort was actually spent.
7. Produce the report with citations, scorecard, session-quality findings, and 1-3 concrete workflow changes.
8. If closure, recap, or roadmap-drainage work is needed, recommend handoff to `daily-review` instead of mutating state here.

## Closure Boundary

Execution-review may cite closure signals as forensic evidence, but it does not own human closure.

Allowed:

- note that a PR merge, issue closure, or session outcome appears relevant to the review
- identify ambiguous closure signals that a human daily review should reconcile
- recommend that `daily-review` drain completed rows or write a human recap
- save execution-review reports/history when requested

Not allowed:

- drain completed roadmap rows
- mark roadmap rows complete
- write day-end human recaps
- route closure writes through `focus`

## Workstream Ribbon

The report should include a chronological ribbon for windowed reviews:

```markdown
| # | Time | Wall | Workstream | Runtime(s) | cwd(s) | Sessions |
|---|------|------|------------|------------|--------|----------|
```

Rules:

- Workstream names are logical workstreams, not repo names or roadmap rows.
- Infer a short workstream label from the request and cwd, and mark it as inferred when the evidence is ambiguous.
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
   - workstream effort, compression, and precision metrics from session aggregates and inspected evidence
4. Inspect representative sessions.
5. Produce the weekly review and 1-3 process experiments.

## Typed Session Review Pipeline

Use this lens when reviewing a Codex session transcript. Apply the same shape to Claude Code when useful, but keep Codex-specific runtime behavior explicit.

| Phase | Review Question |
| --- | --- |
| Intake | Did the agent restate or preserve the user's actual ask, constraints, and latest correction? |
| Orient | Did it read the right local instructions, skill files, repo state, and evidence before asserting conclusions? |
| Plan / Announce | Did it give a bounded plan or working update before meaningful edits or long-running work? |
| Act | Were tool calls scoped, parallelized where useful, and respectful of existing user/concurrent changes? |
| Verify | Did it run focused checks after meaningful edits, and did it report failures or skipped checks plainly? |
| Synthesize | Did it connect evidence to findings, separate facts from recommendations, and avoid overclaiming? |
| Handoff | Did the final response name changed files, residual risk, next actions, and PR/git state accurately? |

Rules:

- Score the session only after inspecting evidence from the phases that matter.
- Cite complete session ids and turn indices when available.
- Treat missing verification after edits as a concrete risk, not a style issue.
- Do not use this pipeline to populate the human daily board; it is an execution-review lens only.
- If the session reveals daily closure work, hand it to `daily-review` instead of performing closure here.

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
