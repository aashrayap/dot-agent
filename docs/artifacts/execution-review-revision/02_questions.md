---
status: in-progress
feature: execution-review-revision
---

# Research Questions: Execution Review Revision

## Codebase

### Q1: What exactly does the current `execution-review` skill do today?
Can the current skill only review Codex sessions, and what inputs, scripts, outputs, and persistence behavior does it currently support?
**Status:** Answered

### Q2: Which parts of the current Codex parser are reusable as the foundation of the revision?
Which responsibilities are already separated cleanly in `codex_sessions.py`, and which parts are tightly coupled to Codex-specific storage or event names?
**Status:** Answered

### Q3: What additional raw signals are already available in local Codex artifacts that the current review skill does not use?
Do existing Codex transcript or state files already expose response-shape, skill invocation, approvals, or other signals useful for presentation and workflow analysis?
**Status:** Answered

### Q4: What local patterns already exist in `~/.dot-agent` for durable state, append-only history, and review/audit loops?
How do `compare`, `projects`, `idea`, and `wiki` currently persist mutable state, and which pattern best fits a revised execution-review system?
**Status:** Answered

### Q5: What parts of the current `look` planning artifacts are still useful evidence, and which assumptions should be treated as stale?
Which previous findings remain grounded in current repo reality, and which prior assumptions have already drifted or were never turned into design?
**Status:** Answered

## Docs

### Q6: What does the local repo documentation say about config ownership, runtime homes, and mutable state boundaries?
What repo rules constrain where review state, config changes, and generated artifacts should live?
**Status:** Answered

### Q7: What does the local wiki skill require from generated outputs?
What frontmatter, file placement, logging, and ingest expectations must the revised execution-review output satisfy?
**Status:** Answered

## Patterns

### Q8: What dimensions should the revised review score, and which of them can be evidence-backed from current telemetry?
How should response presentation, skill usage, verification, workflow efficiency, and recurring failure patterns be separated so the review stays defensible?
**Status:** Answered

### Q9: What is the right boundary between deterministic evidence collection and higher-level interpretation?
Which judgments should come from fixed local metrics first, and which are reasonable to delegate to a second-layer analysis system like Hermes?
**Status:** Answered

### Q10: What is the right durability model for the revised review loop?
Should durable state be a JSONL history, SQLite/DuckDB normalized store, markdown audit log, or some layered combination?
**Status:** Open

### Q11: Is identity splitting (`ash` vs `sushant`) still justified in the revised design?
Does the feature need identity segmentation now, and if so what current mapping source is reliable enough to use?
**Status:** Partially answered

## External

### Q12: How does Hermes actually natively self-improve in the current upstream implementation?
Is the “self-improvement” loop implemented via memory nudges, skill creation, background review, DSPy/GEPA optimization, or some combination?
**Status:** Answered

### Q13: What does Hermes persist natively, and how different is that from what `.codex` exposes?
Does Hermes provide first-class memory, skill, and session layers that materially differ from Codex history/config/rules?
**Status:** Answered

### Q14: Can Hermes natively ingest Codex or Claude Code history, or would that require a custom adapter layer?
If integration is possible, what is native versus what must be custom-built?
**Status:** Answered

### Q15: What parts of Hermes are relevant to this feature versus attractive but orthogonal?
Which Hermes capabilities directly help execution review, and which are part of a broader always-on agent runtime that should remain out of scope?
**Status:** Answered

## Cross-Ref

### Q16: What is the cleanest architecture for combining execution-review evidence with Hermes findings?
Where should Hermes plug in so final reviews can include Hermes insights without making Hermes the source of truth for raw telemetry?
**Status:** Partially answered

### Q17: If Hermes is used as a suggestion or optimization layer, what mutation boundary is safe?
Should Hermes only emit findings, emit proposed diffs, or directly patch shared config and skills?
**Status:** Partially answered

### Q18: What is the smallest shippable revision that materially improves the current system?
What feature slice delivers real value soonest while preserving room for later Hermes-assisted analysis and broader multi-runtime support?
**Status:** Partially answered
