---
status: completed
feature: morning-focus-review-contract
---

# Research: Morning Focus Review Contract

## Flagged Items

### F1. Proposed morning memory intake conflicts with current daily-loop guardrail

Answer: Current `morning-sync` and `focus` contracts explicitly avoid normal reads of project/session state. The proposed workflow can still work, but it needs an explicit contract change that names a lightweight recent-session intake as allowed morning evidence.

Evidence:

- `~/.dot-agent/skills/morning-sync/SKILL.md` says normal input is `~/.dot-agent/state/collab/roadmap.md` and says not to inspect legacy project/session state during the normal morning path.
- `~/.dot-agent/skills/focus/SKILL.md` says focus works in the present and should not inspect legacy project/session state unless the user points to a specific historical artifact.
- `~/.dot-agent/docs/handoffs/human-daily-loop-redesign.md` says the redesign intentionally excludes `execution-review`.

Confidence: high.

Open item: decide whether the new memory intake is default for every `morning-sync`, triggered by stale/empty roadmap, or triggered only when Ash asks for "recent work" context.

### F2. Hermes consumer exists, but no Hermes findings have been generated

Answer: Hermes is currently an optional execution-review findings input, not a producer with observed automated output. The shared findings file exists but has zero lines.

Evidence:

- `~/.dot-agent/skills/execution-review/scripts/write-hermes-findings.py` appends JSONL entries to `~/.dot-agent/state/collab/execution-reviews/hermes-findings.jsonl`.
- `~/.dot-agent/state/collab/execution-reviews/hermes-findings.jsonl` exists, size `0`, modified `2026-04-15 06:24:41 -0500`, and `wc -l` returns `0`.
- `~/.dot-agent/state/collab/execution-reviews/history.jsonl` contains recorded execution reviews with `"hermes_findings": []`.
- Git history shows `write-hermes-findings.py` added in `1a8cc11 Revise execution review workflow` and merged in `92bcc08 Revise execution review workflow (#22)`.

Confidence: high.

Open item: no Hermes producer/automation config was found in the active harness source or state paths searched; only the consumer bridge was found.

### F3. Existing execution-review windows are rolling windows, not "yesterday-weighted" day windows

Answer: `execution-review` supports `day`, `week`, raw hours, and suffixed `h/d/w` windows. It does not currently encode "yesterday first, prior days for context" as a separate selection policy.

Evidence:

- `review_schema.py::parse_window` maps `day` to 24 hours, `week` to 7 days, and accepts `3d`, `36h`, etc.
- `fetch-execution-sessions.py --window 3d` returned a rolling 72-hour selection.
- `aggregate_normalized_sessions` groups by local day after selection, but selection itself is rolling-window based.

Confidence: high.

Open item: morning sync likely needs a small selection layer: local yesterday slice plus a configurable context tail.

## Findings

### Codebase

#### C1. Skill ownership contracts are already aligned with a composed workflow

Answer: Current skill contracts support the desired shape if `morning-sync` becomes the orchestrator, `execution-review` supplies evidence, and `focus` remains the write gate.

Evidence:

- `morning-sync`:
  - Parent: first morning call.
  - Children: `focus`, `idea`, `spec-new-feature`, `excalidraw-diagram`.
  - Reads: `~/.dot-agent/state/collab/roadmap.md`.
  - Writes through: `focus`/`roadmap.py` only when asked for updating sync.
  - Hands off to: `focus`, `idea`, `spec-new-feature`.
- `focus`:
  - Parent: `morning-sync`.
  - Reads: `~/.dot-agent/state/collab/roadmap.md`.
  - Writes through: `skills/focus/scripts/roadmap.py`.
  - Hands off to: `morning-sync`, `daily-review`, `spec-new-feature`.
- `execution-review`:
  - Children: runtime evidence scripts, optional Hermes findings, `excalidraw-diagram`.
  - Reads: Codex/Claude session logs, execution-review evidence/history, PR signals, roadmap rows when relevant, optional Hermes findings.
  - Writes through: execution-review report/history only.
  - Hands off to: `daily-review`, `spec-new-feature`, `focus`, or `review` as recommended follow-up surfaces.

Confidence: high.

Implication: morning sync should not "become execution-review"; it should ask for or run a lightweight evidence intake and then auto-suggest `focus` actions when roadmap changes are warranted.

#### C2. `focus` owns the daily roadmap state and mutation helpers

Answer: `focus` owns `~/.dot-agent/state/collab/roadmap.md`, with legacy `focus.md` kept for compatibility.

Evidence:

- `focus/SKILL.md` names `roadmap.md` as canonical and `focus.md` as legacy compatibility.
- `focus/scripts/roadmap.py` defines `ROADMAP_FILE`, `FOCUS_FILE`, table schemas, statuses, and mutation commands: `setup`, `show`, `focus`, `add`, `status`, `drop`, `review`.
- `morning-sync/scripts/morning-sync-setup.sh` delegates setup to `focus/scripts/focus-setup.sh`, then reports `ROADMAP_SOURCE=human-roadmap` and `PROJECT_STATE_NORMAL_READS=no`.

Confidence: high.

#### C3. Execution-review already has normalized metadata enough for a morning "what you've been working on" table

Answer: The existing adapters can provide thread/session id, runtime, cwd, label, start/end time, wall time, edits, verification count, failures, subagent count, first request excerpt, final response excerpt, skill mentions, and response-fit signals.

Evidence:

- `codex_adapter.py` normalizes Codex thread summaries into `session_id`, `runtime`, `cwd`, `git_branch`, `started_at`, `ended_at`, `wall_seconds`, `model`, `reasoning_effort`, `approval_mode`, `sandbox_policy`, message counts, tool counts, edits, verifications, failures, subagent count, skill mentions, response fit, source ref, and label.
- `codex_sessions.py` reads `~/.codex/state_*.sqlite` and resolves rollouts from `~/.codex/sessions`.
- `claude_adapter.py` reads `~/.claude/projects`, `sessions-index.json`, and `*.jsonl` session logs; it normalizes similar metadata plus entrypoint, permission mode, token usage, and tool categories.
- `review_store.py` persists normalized sessions into `~/.dot-agent/state/collab/execution-reviews/reviews.sqlite`.

Confidence: high.

#### C4. Current three-day evidence confirms the source can see recent Codex and Claude work

Answer: Running the existing setup/fetch path for `3d` found enough recent activity to populate a morning memory table.

Evidence from `execution-review-setup.py 3d`:

- `codex_sessions=41`
- `claude_sessions=10`
- `total_sessions=51`

Evidence from `fetch-execution-sessions.py --runtime all --window 3d`:

- `sessions=51`
- `unique_cwds=12`
- `wall_human=160h41m`
- `edits=16`
- `verifications=25`
- `exec_failures=87`
- `subagent_count=46`
- runtime split: `codex=41`, `claude=10`
- top cwd buckets included:
  - `/Users/ash/Documents/2026/wiki`
  - `/Users/ash/.dot-agent`
  - `/Users/ash/Documents/2026/semi-stocks-2`

Confidence: high.

Note: the fetch command upserted normalized evidence into `reviews.sqlite`; this is normal execution-review behavior.

#### C5. Execution-review already reads roadmap focus context, but morning-sync does not read execution-review context

Answer: The evidence flow exists in one direction today: execution-review can include roadmap context. The reverse direction is not implemented.

Evidence:

- `execution-review/scripts/review_context.py` reads `~/.dot-agent/state/collab/roadmap.md` and extracts focus, in-progress, queued, done, and blocked items.
- `render-execution-review.py` includes a `## Focus Context` section when focus context exists.
- No corresponding helper was found in `morning-sync` that reads execution-review normalized sessions, history, or Hermes findings.

Confidence: high.

#### C6. Hermes setup is a secondary findings bridge under execution-review

Answer: Hermes fits as an optional interpretation channel that writes findings into execution-review state. It should not be treated as raw telemetry and should not directly mutate focus.

Evidence:

- `execution-review/SKILL.md` says Hermes findings are optional additive inputs, not the source of truth for raw telemetry.
- `write-hermes-findings.py` accepts `--window`, `--runtime`, `--title`, `--finding`, `--recommendation`, or `--entry-file`, then appends JSONL.
- `review_store.py::load_matching_hermes_findings` filters Hermes findings by exact `window` and compatible `runtime`.
- `render-execution-review.py` adds a `## Hermes Findings` section only when matching findings exist.

Confidence: high.

### Docs

#### D1. The documented daily loop currently keeps forensic review out of the normal morning path

Answer: The current docs define a roadmap-first daily loop and keep raw runtime/session internals out of morning output.

Evidence:

- `~/.dot-agent/README.md` says the normal day-start surface is the human roadmap, not project/session memory.
- `~/.dot-agent/README.md` says execution-review stays forensic: session quality, verification, skill use, and failure analysis.
- `~/.dot-agent/docs/handoffs/human-daily-loop-redesign.md` says the daily surface should answer focus, active projects, review queue, and parked/blocker questions without session IDs or dependency graphs.

Confidence: high.

#### D2. The skill authoring contract supports this as composition, not a new owner

Answer: The right model is to compose existing owners rather than create another daily-memory skill.

Evidence:

- `~/.dot-agent/skills/references/skill-authoring-contract.md` says prefer composing an existing owner over adding a new top-level skill.
- The ownership map says `focus` owns the daily roadmap and `execution-review` owns forensic retrospective review and session-quality recommendations.
- `~/.dot-agent/skills/README.md` defines "Reads state" as observing another surface without writing it, "Writes through" as mutating through the owning helper, and "Hands off" as transferring ownership to a better surface.

Confidence: high.

### Patterns

#### P1. Auto-suggest `focus`, do not auto-run it

Answer: Existing contracts support `morning-sync` suggesting concrete focus mutations after synthesis, but not silently mutating roadmap state.

Evidence:

- `morning-sync/SKILL.md` says writes happen through `focus`/`roadmap.py` only when the user asks for an updating sync.
- `focus/SKILL.md` says roadmap review is read-only unless the user explicitly asks.
- `skills/README.md` defines `focus` as the owner of `roadmap.md`.

Confidence: high.

#### P2. Morning output must compress session evidence into workstreams

Answer: Execution-review can expose workstream ribbons, but those include full session ids and forensic details that the daily loop intentionally hides. Morning sync should aggregate into human workstream rows and cite evidence lightly.

Evidence:

- `execution-review/SKILL.md` requires complete session ids in forensic reports.
- `morning-sync/SKILL.md` and `focus/SKILL.md` both forbid normal human output from exposing session IDs, dependency graph labels, or raw execution artifact internals.

Confidence: high.

#### P3. Current evidence model can rank threads, but not yet decide "continue/reprioritize" alone

Answer: Available metrics can identify recent work, staleness, failures, missing verification, repeated cwd/workstream activity, and response-fit signals. Ash still needs the final decision prompt because the evidence does not know priority.

Evidence:

- Aggregated fields include wall time, edits, verification count, failures, response-fit feedback signals, and cwd buckets.
- `execution-review` recommendations are grounded in evidence, but `focus` owns current priority judgment and roadmap mutation.

Confidence: high.

### External

No external research needed. All relevant behavior was discoverable in local skill docs, harness docs, scripts, state files, and git history.

Confidence: high.

### Cross-Ref

#### X1. Deduping roadmap rows and session evidence should happen by workstream, not cwd

Answer: `cwd` is useful but insufficient. The evidence layer should combine cwd, first request label, skill mentions, and existing roadmap rows into a short human workstream label.

Evidence:

- `execution-review/SKILL.md` says cwd is a hint only; one repo can hold multiple workstreams and one workstream can span repos/runtimes.
- `render-execution-review.py::_workstream_label` already infers a short label from session label or cwd.

Confidence: high.

#### X2. Hermes should sit behind execution-review, not beside morning-sync

Answer: Hermes should feed execution-review as optional findings. Morning sync can consume a lightweight execution-review intake that may include Hermes findings when present, but should label Hermes as secondary interpretation.

Evidence:

- Hermes findings load only through `review_store.py::load_matching_hermes_findings`.
- `execution-review/SKILL.md` says Hermes is additive and secondary.
- There are currently no Hermes entries to merge.

Confidence: high.

## Patterns Found

- Existing contracts already model the desired ownership split:
  - `morning-sync`: orchestrate day-start synthesis.
  - `execution-review`: gather and interpret runtime evidence.
  - `focus`: mutate the durable daily roadmap.
- The proposed change should alter `morning-sync` from "roadmap-only" to "roadmap plus lightweight recent-work evidence", while preserving a rule against exposing raw session internals.
- The morning block should include `Roadmap mutations proposed` and then auto-suggest `focus` as the next surface for accepted changes.
- Hermes is best treated as a secondary annotation source in the evidence bundle. It should not write roadmap state and should not replace raw Codex/Claude telemetry.
- The current evidence scripts can support a concise `What you've been working on` table, but a new morning-specific summarizer is likely needed to avoid forensic output shape.

## Core Docs Summary

- `~/.dot-agent/README.md`: normal day-start uses `state/collab/roadmap.md`; `morning-sync` reads roadmap, `focus` mutates roadmap, `daily-review` owns closure, `execution-review` stays forensic.
- `~/.dot-agent/docs/handoffs/human-daily-loop-redesign.md`: live daily-loop redesign intentionally kept session IDs, project internals, and execution-review out of normal morning/focus output.
- `~/.dot-agent/skills/README.md`: skill composition should use explicit `Parent`, `Children`, `Reads state`, `Writes through`, `Hands off`, and `Receives back`; human-presenting workflow decisions should use visuals when non-trivial.
- `~/.dot-agent/skills/references/skill-authoring-contract.md`: compose existing owners instead of creating another hidden service layer.
- `~/.dot-agent/skills/execution-review/SKILL.md`: runtime evidence belongs to forensic review; Hermes findings are optional additive input; execution-review can recommend handoffs to `focus`, `daily-review`, `spec-new-feature`, or `review`.

## Open Questions

- Should the morning memory intake run by default, or only when `roadmap.md` is stale/empty or Ash asks for recent-work context?
- What exact window policy should be used: fixed `3d`, local yesterday plus two prior local days, or "since last daily-review" with a maximum cap?
- Should a lightweight execution-review helper be added as a script, or should `morning-sync` call existing `fetch-execution-sessions.py` and perform its own compression?
- What confidence labels should the morning table use when session labels are inferred from first user message or cwd?
- Should Hermes findings appear in the morning table only when they match the selected window/runtime exactly, or should morning sync also show unmatched recent Hermes findings as "context"?
- If a morning sync proposes board changes, should the output include an explicit next command/surface such as "Run `focus` to apply these", or should it invoke `focus` only after Ash says yes?
