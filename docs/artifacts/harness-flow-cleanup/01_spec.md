---
status: draft
feature: harness-flow-cleanup
---

# Feature Spec: Harness Flow Cleanup

## Goal

Simplify the dot-agent operating harness so daily work feels closer to Sushant's
`ROADMAP.md` + `morning-sync` loop while preserving our stronger durable state
boundaries.

The cleanup should make these surfaces feel natural:

- `roadmap.md` or upgraded `focus.md`: lightweight daily operating board.
- `morning-sync`: day-start validation, ingestion, and prioritization.
- `idea`: one composed idea lifecycle with concept, brief, spec, and plan artifacts.
- `projects`: promoted durable project memory, not the default place for every daily task.
- `execution-review`: day-end closure/reconciliation and weekly process review.

## Users and Workflows

Primary user: Ash, using Codex and Claude against the same local dot-agent
install.

### Daily Operating Loop

Ash asks what to work on. The agent should read the daily board, active durable
projects, and recent execution evidence, then update or propose a concise day
shape without requiring a deep `projects` pass.

### Idea Incubation Loop

Ash captures rough ideas, sharpens them into product briefs, optionally creates
a high-level technical spec and a code-grounded plan, then promotes only mature
work into projects.

### Promoted Project Loop

When work becomes durable enough to need execution history, PR tracking, pivots,
or follow-ups, it enters `projects`. Projects should support daily roadmap rows
without forcing every minor task into milestone/session machinery.

### Cleanup Loop

Rare or duplicate skills should be hidden, folded into core skills, or moved to
maintenance-only surfaces. The result should reduce the number of first-class
skills an agent has to choose from.

## Acceptance Criteria

- A canonical daily board exists under `~/.dot-agent/state/collab/` with:
  - a focus statement
  - project-grouped rows
  - `Queued`, `In Progress`, `Completed`, and optionally `Dropped` statuses
  - columns for item, link/ref, idea/spec/project link, and notes
- `focus` becomes the mutation surface for this board, or is renamed/aliased to
  `roadmap`; either way, the user should not need to think about two separate
  day-control files.
- `morning-sync` validates the board, pulls/derives new work candidates when
  possible, surfaces PR/review queues, and proposes the day shape.
- `projects` supports lightweight roadmap-style project rows and does not force
  dependency graphs or deep session blocks unless the work has real sequencing
  complexity.
- `idea` composes Sushant's useful lifecycle parts as modes/artifacts inside one
  skill: `idea.md`, `brief.md`, real idea-level `spec.md`, optional `plan.md`,
  and promotion to roadmap first.
- `spec-new-feature` remains the code-grounded workflow for non-trivial feature
  implementation, but it can consume idea `spec.md` or `plan.md` cleanly.
- `/idea <slug> exec` is retired as a primary mode name or kept only as a
  compatibility alias to `/idea <slug> spec`.
- `execution-review` drains completed roadmap rows, reconciles merged PRs and
  chat evidence, and writes durable review history.
- A usage-based cut list exists for skills that are not frequently used in Codex
  logs, with each candidate marked keep, fold, hide, or cut.

## Boundaries

- Do not merge Sushant's repo wholesale.
- Do not reintroduce `feature-interview`.
- Do not make `ROADMAP.md` a Claude-only runtime file; shared state belongs under
  `~/.dot-agent/state/`.
- Do not turn `roadmap.md` into a full project tracker. It is the daily board.
- Do not delete rarely used strategic skills only because direct Codex invocation
  count is currently zero; classify by usage and role.
- Do not implement the cleanup in this pass unless explicitly requested after
  spec review.

## Risks and Dependencies

- Current `focus.md` exists but is nearly empty; migration must preserve it or
  alias it cleanly.
- Existing `projects` state includes several backfilled or placeholder projects,
  which makes the surface feel heavier than the daily loop needs.
- Usage logs undercount implicit skill use, because many skills trigger from
  natural language rather than explicit `/skill` or `$skill` invocations.
- The new daily board needs deterministic helpers or the agent will keep doing
  fragile markdown surgery.
- If `idea` gains too many sub-artifacts, it can become another overloaded
  system. The split must stay concept/product first, with code-grounded planning
  routed to `spec-new-feature`.
