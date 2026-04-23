---
status: complete
feature: hermes-always-on-thesis
---

# Research: hermes-always-on-thesis

Research source: approved questions in `02_questions.md`.

## Flagged Items

### F1. Hermes is currently a consumer bridge, not an always-on producer

Answer: Existing Hermes support is a JSONL findings bridge consumed by `execution-review` and summarized by `morning-sync`; nothing in the tracked harness currently produces Hermes findings automatically.

Evidence:

- `skills/execution-review/SKILL.md:191-206` defines persistence and a Hermes consumer contract.
- `skills/execution-review/scripts/write-hermes-findings.py:34-50` appends JSONL entries to `state/collab/execution-reviews/hermes-findings.jsonl`.
- `skills/execution-review/scripts/review_store.py:163-182` reads only matching findings by `window` and compatible `runtime`.
- `state/collab/execution-reviews/hermes-findings.jsonl` currently has `0` lines.

Confidence: high.

Open: an always-on producer must be added or configured; the existing bridge only stores findings when something explicitly writes them.

### F2. Current session scoping is not enough for "dot-agent and semi-stocks-2, including everything within"

Answer: The lower-level `execution-review` fetch path can filter Codex sessions by exact `cwd`, but not by repo root descendants or Claude cwd. The `morning-sync` helper has a better git-root mapping pattern that can classify descendant directories across runtimes after fetching.

Evidence:

- `skills/execution-review/scripts/fetch-execution-sessions.py:14-22` exposes `--cwd`, but only passes it to Codex fetch.
- `skills/execution-review/scripts/codex_sessions.py:226-228` filters with exact `cwd = ?`.
- `skills/execution-review/scripts/claude_adapter.py:289-314` fetches Claude sessions by window or session id, not by cwd.
- `skills/morning-sync/scripts/recent-work-summary.py:148-188` resolves git roots from session cwd and maps roots to workstreams.

Confidence: high.

Open: a scoped Hermes intake needs a repo-root filter layer, or it will miss descendant cwd sessions and/or over-include Claude sessions.

### F3. The system has loop-adjacent signals, but no first-class loop detector

Answer: Existing review metrics can see context switches, high-churn low-progress sessions, edit-without-verification, failures, user correction/follow-up signals, and heavy read/no-action behavior. They do not yet classify repeated work as "going in circles" across days, artifacts, or PRs.

Evidence:

- `skills/execution-review/scripts/review_schema.py:253-275` aggregates sessions, unique cwds, wall time, edits, verifications, failures, and context switches.
- `skills/execution-review/scripts/review_scoring.py:176-187` identifies high-churn low-progress sessions.
- `skills/execution-review/scripts/review_scoring.py:259-327` turns failures, feedback, low-progress sessions, and shallow churn into workflow-efficiency recommendations.
- `skills/execution-review/scripts/codex_sessions.py:511-518` emits signals such as edit without verification, heavy read before action, and spawn-heavy.

Confidence: high.

Open: a loop detector needs a small schema for repeated topic/path/goal fingerprints across the two scoped repos.

### F4. Daily human closure exists, but Hermes daily intake/synthesis documents do not

Answer: The harness has day-end recap state under `state/collab/daily-reviews/` and an approved one-day morning working-doc helper, but no Hermes-specific appended intake log or curated thesis/synthesis document.

Evidence:

- `skills/daily-review/SKILL.md:70-82` writes dated daily reviews under `state/collab/daily-reviews/YYYY-MM-DD.md`.
- `skills/focus/scripts/morning-working-doc.py:10-38` writes one dated morning document under `state/collab/morning/YYYY-MM-DD.md`.
- `find state/collab -maxdepth 3 -type d` shows `daily-reviews` and `execution-reviews`, but no Hermes daily directory.

Confidence: high.

Open: first design must choose durable paths for the appended intake log and curated synthesis/thesis.

### F5. Background work should use app/runtime automation, not a tracked daemon

Answer: No tracked harness automation or daemon surface was found. The current Codex app runtime exposes heartbeat and cron automation tooling; heartbeats can attach to this thread and support sub-hour intervals, while cron automations are more constrained.

Evidence:

- Repository search found no tracked `automation` or `heartbeat` source files under `.dot-agent`.
- Current Codex app automation contract in this session supports thread heartbeats and cron automations, with thread heartbeats preferred for continuing work in the same thread.
- `docs/harness-runtime-reference.md:12-15` warns against over-investing in tool-specific tricks likely to be replaced by runtime releases.

Confidence: medium.

Open: design should keep the repo-side Hermes writer independent from the scheduling mechanism, then optionally bind it to a heartbeat.

## Findings

### Codebase

#### C1. Where are Hermes findings generated, stored, read, and displayed?

Answer: They are only generated by explicit calls to `write-hermes-findings.py`; stored in `state/collab/execution-reviews/hermes-findings.jsonl`; read by `review_store.py` and `recent-work-summary.py`; displayed in full execution-review reports or as a tiny morning status.

Evidence:

- Write path: `skills/execution-review/scripts/write-hermes-findings.py:13-50`.
- Storage constant: `skills/execution-review/scripts/review_schema.py:18-24`.
- Execution-review merge: `skills/execution-review/scripts/render-execution-review.py:318-327`.
- Morning status: `skills/morning-sync/scripts/recent-work-summary.py:373-400`.

Confidence: high.

Conflicts: none.

Open: no automated writer exists.

#### C2. Which scripts or skills expect the current Hermes schema?

Answer: The expected entry shape is permissive JSONL with at least `window`, `runtime`, `title`, `findings`, and `recommendations`; matching depends on exact `window` and compatible `runtime`.

Evidence:

- `write-hermes-findings.py:34-43` creates entries with `id`, `source`, `created_at`, `window`, `runtime`, `title`, `findings`, and `recommendations`.
- `review_store.py:176-180` filters entries by exact `window`; runtime `all` can match runtime-specific reviews.
- `render-execution-review.py:318-327` expects `title`, `findings`, and `recommendations`.
- `recent-work-summary.py:387-395` reads `created_at`, `title`, or `id` for the morning status line.

Confidence: high.

Conflicts: no validation layer enforces schema.

Open: daily Hermes documents should not break this JSONL consumer contract.

#### C3. What can run background or recurring work?

Answer: In-repo, no default background runner exists. In the current app runtime, heartbeat automations can wake this thread and cron automations can run recurring jobs. The repo should provide idempotent commands/artifacts and leave scheduling thin.

Evidence:

- Repository search found no tracked automation/heartbeat files.
- Current app automation contract supports heartbeat and cron automations.
- `docs/harness-runtime-reference.md:26-33` says tracked setup should stay source-of-truth and runtime homes are install targets.

Confidence: medium.

Conflicts: runtime automation is app-provided, not tracked repo source.

Open: cadence and wakeup style should be a design choice, not embedded into the first data model.

#### C4. What current helpers create per-day documents?

Answer: `daily-review` writes day-end recaps; `morning-working-doc.py` writes approved one-day focus packets. Neither is a Hermes append log or curated synthesis.

Evidence:

- `skills/daily-review/SKILL.md:70-82` documents `state/collab/daily-reviews/YYYY-MM-DD.md`.
- `skills/focus/scripts/morning-working-doc.py:41-72` renders a dated focus document with goal, evidence, docs, next step, and gate.

Confidence: high.

Conflicts: none.

Open: Hermes likely needs separate daily state to avoid overloading human daily review.

#### C5. Which surfaces own mutations?

Answer: `focus` owns roadmap mutations; `daily-review` owns human closure and completed-row drainage through `roadmap.py`; `execution-review` owns forensic reports/history only; `morning-sync` is read-mostly and routes writes through `focus`.

Evidence:

- `skills/focus/SKILL.md:16-22` and `64-70`.
- `skills/daily-review/SKILL.md:13-21` and `110-121`.
- `skills/execution-review/SKILL.md:13-16` and `78-95`.
- `skills/morning-sync/SKILL.md:15-21` and `159-170`.
- `skills/README.md:113-135` states the composability ownership model.

Confidence: high.

Conflicts: none.

Open: Hermes suggestions should remain suggestions unless routed through the owning surface.

#### C6. Where are raw internals filtered from human-facing output?

Answer: `morning-sync`, `daily-review`, and the human daily loop docs explicitly forbid session IDs, dependency graph labels, project anchors, and raw execution internals in normal human output.

Evidence:

- `skills/morning-sync/SKILL.md:50-56` and `167-170`.
- `skills/daily-review/SKILL.md:149-158`.
- `docs/handoffs/human-daily-loop-redesign.md:30-39` and `67-85`.

Confidence: high.

Conflicts: full `execution-review` reports intentionally include session IDs for forensic review (`skills/execution-review/SKILL.md:96-112`).

Open: Hermes daily log can keep machine-readable details locally, but human presentation must distill them.

### Docs

#### D1. What do runtime docs imply?

Answer: Keep shared behavior in tracked source, keep machine-local state under `state/`, and avoid fragile runtime-home patches or overbuilt tool-specific background tricks.

Evidence:

- `docs/harness-runtime-reference.md:17-24` defines tracked source vs gitignored state vs runtime homes.
- `docs/harness-runtime-reference.md:26-33` defines setup/source-of-truth rules.

Confidence: high.

Open: design should put reusable Hermes scripts in `skills/.../scripts` or another tracked source path, with daily outputs in `state/`.

#### D2. What do workflow skill docs say about boundaries?

Answer: Daily/morning/focus surfaces are human-readable and roadmap-centered. Execution review is forensic. Hermes is currently secondary interpretation inside execution-review, not a daily-loop owner.

Evidence:

- `skills/execution-review/SKILL.md:36-57`.
- `skills/morning-sync/SKILL.md:27-37`.
- `skills/daily-review/SKILL.md:23-31`.
- `skills/focus/SKILL.md:35-52`.

Confidence: high.

Open: Hermes always-on should annotate workflow, not replace these owners.

#### D3. Existing docs define Hermes as reviewer/advisor, not planner

Answer: Prior execution-review design treats Hermes as optional, file-contract-first, and secondary to raw telemetry.

Evidence:

- `docs/artifacts/execution-review-revision/04_design.md:207-238` says Hermes can read normalized review outputs and append additive findings, with an MCP bridge later.
- `docs/artifacts/morning-focus-review-contract/03_research.md:24-37` found no generated Hermes findings and no producer.

Confidence: high.

Open: current feature can promote Hermes from optional review add-on to default workflow advisor, but should preserve secondary status.

### Patterns

#### P1. Existing artifact pattern supports a central landing page plus phase docs

Answer: `spec-new-feature` already uses `00_summary.md` plus phase artifacts for durable planning. That is suitable for feature planning, not necessarily for daily Hermes operation.

Evidence:

- `skills/README.md:223-230` describes `spec-new-feature` artifact sets and `daily-review` retained records.
- Current `docs/artifacts/*` directories use summary/spec/questions/research/design/tasks files.

Confidence: high.

Open: Hermes daily operation should avoid creating feature-artifact clutter for every day.

#### P2. Existing scripts separate raw evidence from human synthesis

Answer: Execution-review stores normalized evidence/history and renders a report; morning-sync compresses that into a small workstream table; daily-review writes a human recap from roadmap rows.

Evidence:

- `skills/execution-review/scripts/fetch-execution-sessions.py:53-66` stores normalized sessions and returns aggregate JSON.
- `skills/execution-review/scripts/render-execution-review.py:225-340` renders forensic report sections.
- `skills/morning-sync/scripts/recent-work-summary.py:410-420` classifies stream state into human labels.
- `skills/daily-review/SKILL.md:84-108` defines human daily recap shape.

Confidence: high.

Open: Hermes two-doc model can follow the same separation: append log for machine/detail, curated synthesis for human and workflow use.

#### P3. Existing loop indicators are metric-based, not thesis-based

Answer: Current review logic can flag shallow churn, high context switching, and missing verification, but it does not compare activity to a central thesis or intended workflow.

Evidence:

- `review_scoring.py:143-187` derives review signals from aggregate metrics.
- `review_scoring.py:313-327` emits generic recommendations from low scores.
- No searched file defines a central Hermes thesis or daily thesis document.

Confidence: high.

Open: a central thesis can be the missing comparator for "going in circles."

### External

#### E1. Background capability is available at app level, not repo level

Answer: Current Codex app context supports thread heartbeat automations and cron automations. For this feature, a thread heartbeat is the simpler "background in this conversation" mechanism; a cron job is better only if the work should happen in a separate conversation/workspace.

Evidence:

- Current app automation tool contract supports `kind="heartbeat"` with `destination="thread"` and minute/daily/weekly schedules.
- Current app automation guidance says to prefer thread automations in most cases.

Confidence: medium.

Conflicts: app automation behavior is not documented in tracked repo files.

Open: implementation should not require automation to be present; it should expose a script/prompt that an automation can run.

#### E2. Persistence/privacy limits

Answer: Local daily operational notes should stay under gitignored `state/`, not tracked docs, unless a human explicitly promotes them. Human surfaces must avoid raw session IDs and transcript internals by default.

Evidence:

- `docs/harness-runtime-reference.md:17-24` places reviews and tool caches under gitignored `state/`.
- `morning-sync` and `daily-review` rules forbid raw internals in normal output.

Confidence: high.

Open: define retention and whether the appended log can include local-only stable identifiers.

### Cross-Ref

#### X1. Relationship to roadmap, morning sync, daily review, and execution review

Answer: Roadmap remains canonical for commitments. Execution-review remains canonical for raw/normalized telemetry. Hermes daily log/synthesis should be an advisory layer that compares scoped execution evidence against a central thesis, then feeds tiny status to morning sync and optional closure context to daily review.

Evidence:

- Ownership model in `skills/README.md:113-135`.
- Execution-review persistence in `skills/execution-review/SKILL.md:191-206`.
- Daily loop target model in `docs/handoffs/human-daily-loop-redesign.md:41-63`.

Confidence: high.

Open: exact file paths and merge points need design.

#### X2. Minimum schema for first useful Hermes daily findings

Answer: Existing consumers need the old JSONL finding fields. The new daily model needs, at minimum, date, scope, thesis version/text, evidence window, loop/drift/gate observations, suggested action text, and presentation-safe summary.

Evidence:

- Existing JSONL writer fields in `write-hermes-findings.py:34-43`.
- Existing morning display only needs count/title in `recent-work-summary.py:373-400`.
- User direction requires two documents: appended log and curated synthesis/thesis.

Confidence: medium.

Open: design must decide whether the old `hermes-findings.jsonl` remains the only machine-readable stream or whether daily log entries also feed it.

#### X3. Authority when thesis, roadmap, and evidence disagree

Answer: Current repo conventions imply roadmap owns commitments, execution evidence owns what happened, and Hermes owns advisory interpretation. Disagreement should produce a flagged item, not a mutation.

Evidence:

- `focus` owns roadmap state and present focus (`skills/focus/SKILL.md:41-52`).
- `execution-review` says Hermes findings are additive and secondary (`skills/execution-review/SKILL.md:44` and `184`).
- `morning-sync` must not auto-add inferred work to roadmap (`skills/morning-sync/SKILL.md:70-82`).

Confidence: high.

Open: define the exact conflict labels in synthesis.

#### X4. Migration path to default-on

Answer: The safest migration is: first define repo-scoped daily log/synthesis generation; then wire a thin default-on trigger; then optionally feed summaries into morning/daily surfaces. Direct auto-mutation or Hermes-as-primary-runtime should stay out of the first slice.

Evidence:

- Current Hermes bridge is optional and file-based.
- Current runtime docs warn against over-investing in tool-specific tricks.
- Current human daily loop keeps forensic details out of normal daily surfaces.

Confidence: medium-high.

Open: background trigger still needs a concrete design choice.

## Patterns Found

- File-contract-first integration fits this repo better than a new service.
- Human-readable daily surfaces stay separate from forensic evidence.
- Roadmap mutation flows through `focus`, not advisory layers.
- Existing metrics can seed loop detection, but a thesis comparator is missing.
- `state/` is the right home for daily Hermes output; tracked docs are the right home for the design/spec only.

## Core Docs Summary

- `harness-runtime-reference.md`: tracked repo owns shared behavior; `state/` owns machine-local daily/review outputs; avoid brittle runtime-home hacks.
- `skills/README.md`: every skill has an owner; state writes go through the owning helper.
- `execution-review/SKILL.md`: forensic evidence and Hermes findings live under execution-review state; Hermes is additive.
- `morning-sync/SKILL.md`: day-start surface is concise, hides raw internals, and shows Hermes only as tiny status.
- `daily-review/SKILL.md`: day-end human closure writes dated recaps and drains completed roadmap rows.
- `human-daily-loop-redesign.md`: daily board must be plain-language and should not expose session IDs, dependency graphs, or project internals.

## Direction Options

### Option A. Minimal Daily Hermes File Contract

Create a simple scoped intake/synthesis flow:

- append local daily intake entries under `state/collab/hermes/daily/YYYY-MM-DD-log.jsonl` or equivalent
- maintain curated daily synthesis under `state/collab/hermes/daily/YYYY-MM-DD.md`
- keep existing `hermes-findings.jsonl` as compatibility output for execution-review/morning status
- schedule later through app heartbeat or run manually first

Pros: simplest, fits user direction, preserves current ownership.
Cons: requires new doc/schema; background trigger still separate.

### Option B. Extend Execution-Review Only

Keep all Hermes output under `state/collab/execution-reviews/`, adding loop-detection summaries and writing findings into existing JSONL.

Pros: least new state surface.
Cons: weak fit for daily thesis/synthesis; risks turning execution-review into daily memory.

### Option C. Real Hermes Runtime Bridge

Integrate Hermes native memory/session model or MCP-style bridge and let Hermes perform analysis directly.

Pros: most aligned with "Hermes" as an external/native advisor.
Cons: higher complexity, likely beyond "keep it simple"; prior research says Hermes does not natively ingest Codex/Claude history.

### Research Default

Option A looks best for the first design slice: simple local daily docs, scoped to `dot-agent` and `semi-stocks-2`, with suggestions only and no roadmap mutation.

## Open Questions

1. Should the first background trigger be a thread heartbeat, or should the first implementation only create an idempotent manual command and leave scheduling as a follow-up?
2. Should the curated synthesis be one file per day, or should there also be one rolling central thesis file that the daily synthesis updates by reference?
3. What is the smallest useful loop detector: repeated topic labels, repeated cwd/workstream switching, repeated failed gates, or repeated user corrections?
4. Should compatibility writes to `hermes-findings.jsonl` happen for every daily synthesis, or only when Hermes detects a gate/loop worth surfacing?
