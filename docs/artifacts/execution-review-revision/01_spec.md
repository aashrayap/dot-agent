---
status: draft
feature: execution-review-revision
---

# Feature Spec: Execution Review Revision

## Goal

Replace the current Codex-only `execution-review` skill and the obsolete unified-review draft with a full reflection system that:

1. analyzes real work across Codex and Claude Code from local session artifacts
2. evaluates response quality, skill usage, and workflow efficiency with explicit evidence
3. supports a second-layer analysis path for Hermes findings without confusing Hermes memory with raw session telemetry
4. produces durable history, trend detection, and wiki-ready outputs from a single review flow

This revision should treat the current planning artifacts under `docs/artifacts/look/` as superseded research input, not as the source of truth for the new design.

## Users and Workflows

**Primary user:** Ash, using Codex locally today and potentially Hermes as an always-on analysis or orchestration layer.

**Secondary user:** Sushant, if identity segmentation remains valuable after redesign.

### Core workflows

1. **Daily execution review**
   Review the last day of work across Codex and Claude Code, identify what consumed time, how responses landed, where skills helped or were missed, and what concrete changes to test next.

2. **Weekly optimization review**
   Analyze trends across several days: context switching, verification quality, repeated mistakes, response presentation drift, and changes in skill usage.

3. **Hermes-assisted retrospective**
   Feed normalized review outputs into Hermes so Hermes can surface higher-level patterns, repeated workflow suggestions, or optimization ideas as a secondary analysis layer.

4. **Session deep dive**
   Inspect a specific session or thread to explain why a task went well or poorly, with evidence from commands, edits, verification, and assistant behavior.

5. **Continuous improvement loop**
   Save review outputs in durable machine-readable history, compare newer reviews to past recommendations, and track whether suggested changes were adopted and improved outcomes.

6. **Wiki filing**
   Emit review results and durable insights in a format that can be filed into the local wiki through the existing `/wiki ingest` workflow.

## Scope

**In scope:**
- Codex session analysis from local SQLite and rollout JSONL
- Claude Code session analysis from local project JSONL stores
- review dimensions for:
  - response presentation quality
  - skill usage quality
  - workflow efficiency and verification discipline
  - recurring failure patterns
- durable review history and trend comparison
- Hermes findings as an additive analysis section
- wiki-ready output
- a fresh rewrite of planning artifacts for this feature

**Out of scope:**
- replacing Codex or Claude Code as the primary coding runtime
- assuming Hermes becomes the system of record for raw telemetry
- direct autonomous mutation of shared runtime config without explicit review
- UI/dashboard work beyond markdown and local state files
- browser automation or messaging automation unrelated to the review loop itself

## Acceptance Criteria

### Review system
- The revised skill can analyze Codex sessions and Claude Code sessions from local artifacts in a single review flow.
- The review output distinguishes raw evidence from interpreted recommendations.
- The review includes explicit analysis of:
  - response presentation quality
  - skill usage and missed opportunities
  - verification behavior
  - workflow fragmentation or focus
  - recurring mistakes or rework

### Hermes integration
- The design explicitly documents how Hermes natively self-improves today.
- Hermes findings are treated as a secondary analysis layer, not as a replacement for raw session evidence.
- The system can include Hermes findings in final execution reviews without requiring Hermes to be the primary runtime.

### Durability
- Reviews write durable history under `~/.dot-agent/state/` rather than only ephemeral markdown output.
- The system can compare new reviews against prior review entries and prior proposed changes.
- The review can produce wiki-ready markdown that matches the existing wiki contract.

### Revision quality
- The obsolete `look` planning direction is replaced by a fresh spec, research set, design, and task breakdown for this feature.
- The final task plan is executable without relying on the old artifact set as the active plan.

## Boundaries and Non-Goals

- The system should not pretend that `.codex` exposes a Hermes-style memory substrate if it only exposes logs, config, and session history.
- The system should not depend on undocumented vendor behavior unless research confirms the current implementation.
- The system should not silently collapse “Codex findings” and “Hermes findings” into one undifferentiated score.

## Risks

- Claude Code and Codex expose asymmetrical telemetry, which may distort a shared scorecard if handled poorly.
- Hermes marketing language may not match the actual implementation of its self-improvement loop.
- Identity splitting (`ash` vs `sushant`) may add complexity without enough signal if mapping remains ambiguous.
- Existing execution-review heuristics may be too brittle for presentation-quality judgments unless the evidence model is widened.

## External Dependencies

- Local Codex runtime artifacts under `~/.codex/`
- Local Claude Code artifacts under `~/.claude/`
- Hermes upstream repo and docs for current self-improvement behavior
- Local wiki workflow under `~/Documents/2026/wiki/`
