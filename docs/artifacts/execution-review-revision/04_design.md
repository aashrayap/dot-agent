---
status: draft
feature: execution-review-revision
---

# Design: Execution Review Revision

## Design Overview

The revised execution-review system will be an **evidence-first reflection pipeline** rooted in `~/.dot-agent/state/`, with Hermes treated as an **optional secondary analysis layer** rather than the source of truth for raw telemetry.

The design keeps three layers distinct:

1. **Collection and normalization**
   Read Codex and Claude Code local artifacts, reduce them into a shared session model, and persist normalized evidence locally.

2. **Review and scoring**
   Build daily/weekly reviews from the normalized evidence store, generate defensible scorecards, emit structured history, and produce wiki-ready markdown.

3. **Hermes findings**
   Allow Hermes to consume normalized review outputs and produce additive findings, recommendations, or experiments without taking over evidence collection.

```text
raw runtimes (.codex / .claude)
        ↓
runtime adapters
        ↓
normalized local evidence store
        ↓
execution review + scorecard + history
        ↓
optional Hermes findings
        ↓
final report / wiki-ready output
```

## Relevant Repo Principles

These repo principles shaped the design:

- Shared source of truth lives in `~/.dot-agent/`, not runtime homes.
- Mutable artifacts belong under `~/.dot-agent/state/`.
- Shared skill content should avoid hardcoded runtime-home assumptions where possible.
- Existing patterns favor append-only logs, auditable history, and explicit human review over silent mutation.

## Decision Log

### D1: Execution review remains the evidence system of record

**Decision**

Execution review will remain the primary evidence and scoring system. Hermes will not be used as the primary collector or judge of Codex/Claude telemetry.

**Options considered**

- Hermes as the primary review runtime
- Symmetric merge of execution review and Hermes from the start
- Execution review as primary evidence layer, Hermes as optional secondary consumer

**Rationale**

The repo already has a strong deterministic parser foundation for Codex, while Hermes is native to its own session/memory model and does not currently ingest Codex/Claude history stores natively. Keeping execution review as the source of truth preserves auditability and keeps the core review loop independent.

**Affected areas**

- `skills/execution-review/`
- `~/.dot-agent/state/collab/execution-reviews/`
- final report shape

**Risks still open**

- Hermes findings may be tempting to over-weight relative to raw evidence if the final report is not clearly segmented.

### D2: Introduce runtime adapters over a shared normalized model

**Decision**

The new system will use **runtime adapters**:

- `CodexAdapter`
- `ClaudeAdapter`

Both adapters will emit a shared normalized session schema consumed by the review layer.

**Options considered**

- Keep a single monolithic parser and branch by runtime
- Maintain two completely separate review systems
- Use per-runtime adapters over a shared normalized schema

**Rationale**

The current parser already separates thread selection, per-thread summarization, and aggregation. Adapters preserve that shape while isolating schema-specific logic.

**Affected areas**

- new scripts under `skills/execution-review/scripts/`
- current `codex_sessions.py` split/refactor
- future shared setup/fetch/inspect entrypoints

**Risks still open**

- Claude Code session schema drift remains a parser risk.

### D3: Use layered durability, not a single storage format

**Decision**

The revised system will use a layered local state model under `~/.dot-agent/state/collab/execution-reviews/`:

- `reviews.sqlite` — normalized evidence store and query layer
- `history.jsonl` — append-only review history entries
- `reports/` — saved human-readable markdown reviews
- `hermes-findings.jsonl` — optional additive analysis layer if/when Hermes is used

**Options considered**

- Markdown-only history
- JSONL-only history
- SQLite/DuckDB-only design
- layered storage

**Rationale**

Markdown alone is weak for trend queries; DB-only is weak for append-only audit narrative; JSONL alone becomes awkward for flexible joins and per-session lookup. SQLite is already a strong fit in this repo and requires no new heavy dependency.

**Affected areas**

- `~/.dot-agent/state/collab/execution-reviews/`
- storage helper script/module
- report writer

**Risks still open**

- Need to keep `history.jsonl` and `reviews.sqlite` synchronized cleanly.

### D4: Replace the old scorecard with a workflow-optimization scorecard

**Decision**

The revised review will score:

1. **Focus**
2. **Grounding**
3. **Verification**
4. **Response Fit**
5. **Skill Leverage**
6. **Workflow Efficiency**

Recurring mistakes will be tracked as a first-class review section and history signal, but not as a separate scored dimension in the initial rewrite.

**Options considered**

- Keep the current 5-dimension scorecard
- Keep the obsolete `look` scorecard
- Expand to a new 6-dimension workflow-optimization scorecard

**Rationale**

The user’s stated goals are response presentation, skill usage, and workflow optimization. The old and obsolete scorecards only partially cover those concerns. Separating recurring mistakes from the scored dimensions keeps the scorecard defensible while still tracking recurrence explicitly.

**Affected areas**

- report templates
- scoring module
- history schema

**Risks still open**

- Response Fit is harder to operationalize rigorously than the other dimensions.

### D5: Response Fit will be based on an extracted evidence bundle, not raw vibes

**Decision**

Response presentation quality will be evaluated from an explicit evidence bundle per reviewed session:

- first user request
- final assistant response excerpt
- commentary/final message mix
- user follow-up count
- user correction phrases when present
- interruptions or terse “redo/concise” style feedback where available

The review layer may still interpret these signals, but the evidence bundle must always be shown or derivable.

**Options considered**

- Defer response presentation entirely
- Purely LLM-score raw session text
- Extract a deterministic response-fit evidence bundle first, then judge it

**Rationale**

Response quality matters to the feature goal, but the review must remain evidence-backed. This design gives the review enough material to judge response quality without making the whole scorecard subjective.

**Affected areas**

- runtime adapters
- per-session normalized schema
- inspect/deep-dive outputs

**Risks still open**

- Need careful heuristics for “user correction phrases” to avoid false positives.

### D6: Hermes integration is optional and file-contract-first

**Decision**

Hermes integration will be **optional** in the core design. The first integration contract will be file-based:

- execution review writes normalized history/results locally
- Hermes can read those artifacts and append additive findings
- execution review can merge Hermes findings into the final report when available

An MCP bridge can be added later, but it is not required for the first full revision.

**Options considered**

- Hard dependency on Hermes for final reviews
- No Hermes integration at all
- Optional Hermes integration via local file contract first

**Rationale**

Hermes is valuable as an advisor layer, but the current upstream repo does not natively ingest Codex/Claude histories. A file contract keeps the first revision shippable and decoupled.

**Affected areas**

- review history schema
- final report sections
- future Hermes skill/MCP bridge

**Risks still open**

- Need a stable matching key for tying Hermes findings to a review window.

### D7: Identity mapping becomes optional, default-off

**Decision**

Identity segmentation (`ash` vs `sushant`) will be supported as an optional config layer, but not required for the first working system.

Default behavior:

- no identity split
- everything lands in a single default bucket

Optional behavior:

- path-based mapping config when the user wants it

**Options considered**

- Keep identity mandatory
- Drop identity entirely
- Make identity optional with default-off behavior

**Rationale**

There is no current repo-backed identity mapping implementation. Treating it as optional avoids blocking the rewrite on an unsupported assumption while preserving room for later segmentation.

**Affected areas**

- local config file for review state
- normalized schema
- report breakdown sections

**Risks still open**

- If identity becomes important later, retroactive backfill may be partial.

### D8: The skill becomes dual-runtime with thin wrappers and a shared core

**Decision**

`execution-review` will be upgraded to a dual-runtime skill using the repo’s standard pattern:

- shared root `SKILL.md` for common intent and output contract
- thin `claude/` and `codex/` wrappers only where runtime-specific framing differs
- shared scripts in `scripts/`

**Options considered**

- Keep Codex-only skill
- Duplicate the whole skill separately for Claude and Codex
- Shared core plus thin runtime wrappers

**Rationale**

This matches existing repo conventions (`review`, `spec-new-feature`, `compare`) and keeps behavior aligned across runtimes while allowing small runtime-specific entry adjustments.

**Affected areas**

- `skills/execution-review/skill.toml`
- `skills/execution-review/SKILL.md`
- `skills/execution-review/codex/SKILL.md`
- `skills/execution-review/claude/SKILL.md`

**Risks still open**

- Need to keep wrapper behavior genuinely thin so the shared logic does not fork again.

### D9: Hooks are additive, not a prerequisite for V1

**Decision**

The first full revision will **not require Codex hooks** to be useful.

If hooks are later added, they will be treated as supplemental sensors for richer telemetry, not as the only source of review data.

**Options considered**

- Make hooks mandatory
- Ignore hooks entirely
- Keep hooks out of V1 but allow later enrichment

**Rationale**

There is no tracked hook system in the current repo-side Codex setup. Existing runtime artifacts are already sufficient to materially improve execution review.

**Affected areas**

- review bootstrap
- future observability extensions

**Risks still open**

- Some presentation or turn-level feedback signals may remain weaker without hook data.

### D10: The old `look` plan is retained only as legacy research

**Decision**

The `docs/artifacts/look/` set will be treated as legacy research input only. It will not be resumed as the active plan.

**Options considered**

- Resume `look`
- Delete `look`
- Retain `look` as legacy evidence and replace it with a fresh active artifact set

**Rationale**

The research is still useful, but the plan drift is too large to treat it as the active feature track.

**Affected areas**

- documentation only

**Risks still open**

- None beyond potential confusion if both artifact sets are not clearly distinguished.

## Files and Areas Expected to Change

- `skills/execution-review/skill.toml`
- `skills/execution-review/SKILL.md`
- `skills/execution-review/codex/SKILL.md`
- `skills/execution-review/claude/SKILL.md` (new)
- `skills/execution-review/scripts/`
  - refactor current Codex parser
  - add Claude adapter
  - add shared normalized storage/report helpers
- `~/.dot-agent/state/collab/execution-reviews/`
  - new durable storage layout

## Risks Still Open

- Exact normalized schema details for response-fit analysis
- Exact `history.jsonl` shape and DB schema
- Hermes findings merge key and lifecycle
- Whether identity remains out of the first ship or comes back via config
