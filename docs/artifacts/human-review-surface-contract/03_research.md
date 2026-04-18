---
status: complete
feature: human-review-surface-contract
---

# Research: human-review-surface-contract

## Flagged Items

- The previous daily loop leaked `projects/*` internals into `morning-sync` and
  `focus` output. The concrete bad surface was session labels such as `S01`,
  `S02`, dependency graph labels, and `project.md#s01` anchors appearing in
  human-facing day-start output.
- `execution-review` previously mixed forensic session review with human closure
  and roadmap drainage. That made day-end closure harder to distinguish from
  agent-quality review.
- Excalidraw was added as a durable diagram skill, but the broader
  visual-first presentation rule initially lived only in planning artifacts.
- The Excalidraw renderer previously followed upstream `main`, which was too
  unstable for a primary human review surface.

## Findings

- The root review surface should be `README.md`, `AGENTS.md`, and diagrams.
- The skill review surface should be `skills/README.md`, `skills/AGENTS.md`,
  individual `SKILL.md` files, and `skill.toml`.
- Human daily workflow should be owned by `morning-sync`, `focus`, and
  `daily-review` over `state/collab/roadmap.md`.
- Forensic session review should remain in `execution-review`; it can recommend
  daily closure, but it should not mutate the daily board.
- Deep implementation planning belongs in `spec-new-feature`; durable execution
  history belongs in `projects` only when explicitly needed.
- Human-presenting skills should lead with or point to a diagram when explaining
  workflow, architecture, planning, review, or proposed state.
- Code review should be risk-triggered, not hidden. Runtime setup, renderers,
  state mutation, adapters, and generated outputs still need code sampling.

## Patterns Found

- Diagram first, text second works best for human understanding of workflow and
  architecture.
- Agent-facing contracts should remain terse and generic. Human-facing docs can
  carry richer visual and review-surface guidance.
- Daily board state needs plain-language rows grouped by project/workstream,
  review queue, and parked/blocked work.
- Session IDs and dependency graphs remain useful in deep artifacts, but they
  should not appear in the normal day-start or focus output.

## Core Docs Summary

## Open Questions
