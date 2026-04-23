---
status: draft
feature: harness-reduction
---

# Feature Spec: harness-reduction

## Goal

Reduce Ash's agent harness after an experimentation cycle, keeping only the
highest-leverage structure before the next deliberate expansion cycle.

The target is a leaner portable harness across:

- `/Users/ash/.dot-agent`
- `/Users/ash/.dot-codex`

Primary thesis:

1. Lock down a very concise repo-level agent instruction surface that works
   across most repos and situations.
2. Give each skill an explicit composability schema so it knows where it fits
   in the wider workflow stack.
3. Remove token leakage from the orchestrator path so early session context is
   spent on excellent specs, handoffs, research packets, and next-session
   setup instead of repeated harness exposition.

## Users and Workflows

- Ash uses Codex as the preferred runtime while keeping the harness portable to
  Claude Code.
- Codex and Claude Code consume repo instructions, skills, and harness state to
  plan, review, execute, and hand off work.
- Long-lived workflows move through idea, focus, feature spec, execution,
  review, daily closure, and external handoff.
- The intended loop is cyclical: bloat through experimentation, prune to the
  best primitives, then allow the next round of experimentation.

## Acceptance Criteria

- Root instruction surfaces are materially shorter while preserving the
  strongest operating principles.
- Repeated guidance is removed or moved behind progressive disclosure.
- Skill files share a compact composability schema or a clear rule for when the
  schema is required.
- Orchestrator-token leaks are identified and categorized by source.
- The reduction plan distinguishes:
  - keep as core
  - move behind skill or doc lookup
  - archive/delete
  - defer until next bloat cycle
- Verification path is defined before execution, including any setup/audit step
  needed to keep installed payloads from drifting.

## Boundaries

- Do not delete or rewrite working harness pieces before research identifies
  their current role and install path.
- Do not optimize only for token count if it removes durable judgment,
  cross-runtime portability, or critical safety constraints.
- Do not bury daily-use instructions so deeply that agents fail common tasks.
- Keep machine-local private context, risky permission bypasses, and one-off
  local overrides out of tracked config.
- Keep Codex bias explicit, but do not make the harness unusable for Claude Code
  unless Ash deliberately chooses that tradeoff.

## Human Direction

- Ash sees the founding principles as still strong; reduction should preserve
  the North Star, not start from scratch.
- Codex is the preferred runtime right now.
- The next iteration should treat prompt/context optimization as a compounding
  advantage, especially in the first 0-200k tokens of a session.
- Skill composability should become an intentional system property, not ad hoc
  prose.
- The work should begin with back-and-forth direction questions before codebase
  research.

Direction update, captured 2026-04-23:

- Scope is the whole harness, with `.dot-agent` as source and Codex runtime
  surfaces as consumers.
- `.dot-codex` should be considered through `.dot-agent` changes and setup
  behavior; direct runtime changes are only justified when research proves source
  changes are insufficient.
- Principled locations are a first-order goal: clean root agent instructions,
  consistent skill structure and composability, and docs living where Ash knows
  to look.
- Token budget should start flexible; research should produce a realistic range
  and a separate smoke-test view of current context shape.
- Priority order is Codex-first ergonomics, durable planning quality, then
  portability.
- Experimental material can be deleted because git history exists, but an
  archive note with commit references may be useful for intentionally removed
  material.
- Every skill should eventually get structure and composability, but this pass
  should focus on foundational pattern before parallel application across all
  skills.
- Produce a before/after diagram after design and before implementation.
- Use subagents where possible to keep orchestrator context clean.
- Treat deterministic scripts, schemas, and subagent packets as preferred ways
  to reduce orchestrator context pollution.

Open choices:

- What is the right token range for root instructions after current shape is
  measured?
- What is the smallest composability schema that every skill can carry without
  bloat?
- Which deterministic checks or scripts should become the foundation for future
  harness pruning?
- What archive format, if any, is worth keeping for deleted experimental
  material?

## Risks and Dependencies

- Over-compression can remove judgment that prevents bad edits, poor reviews,
  or instruction drift.
- Under-compression leaves the orchestrator path bloated and weakens the
  workflowmaxxing thesis.
- Cross-runtime differences can cause Claude and Codex surfaces to diverge.
- Skill install/setup mechanics may require changes after source files are
  reduced.
- Current repo state may contain useful experimental artifacts that should be
  archived instead of deleted.
