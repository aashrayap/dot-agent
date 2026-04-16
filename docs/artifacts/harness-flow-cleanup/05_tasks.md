---
status: draft
feature: harness-flow-cleanup
---

# Tasks: Harness Flow Cleanup

## Execution Order

| ID | Task | Depends On | Est. Hours | Notes |
|----|------|------------|------------|-------|
| T01 | Add shared roadmap state and compatibility loader | - | 2 | Establish `roadmap.md` without breaking `focus.md` |
| T02 | Update `focus` into roadmap mutation surface | T01 | 3 | View/add/edit/reorder/status/drop rows |
| T03 | Update `morning-sync` to validate and update roadmap | T01, T02 | 3 | Sushant-style day-start loop, shared-state version |
| T04 | Simplify new `projects` scaffold defaults | T01 | 2 | Shallow by default, deep only when warranted |
| T05 | Compose `idea` artifacts | - | 4 | Add `spec.md` and optional `plan.md` modes cleanly |
| T06 | Add execution-review drain contract for roadmap rows | T01, T03 | 3 | Completed rows drain into recap and project execution memory |
| T07 | Merge agent instruction doc skills and hide rare maintenance surfaces | - | 3 | Keep create-agents-md, fold improve-agent-md into it |
| T08 | Add skill composition contract | - | 2 | Require Composes With for retained/new skills |
| T09 | Run setup, smoke tests, and update docs | T02, T03, T04, T05, T06, T07, T08 | 2 | Verify runtime copies and docs |

## Task List

### T01: Add shared roadmap state and compatibility loader

Implement:

- Add or update helper logic so `~/.dot-agent/state/collab/roadmap.md` is the
  canonical daily board.
- Preserve existing `focus.md` by migrating or reading it as a fallback.
- Create an initial roadmap from current `focus.md` when no roadmap exists.

Acceptance criteria:

- Fresh setup creates or resumes a readable daily board.
- Existing `focus.md` users are not stranded.
- No project state is modified by a read-only setup path.

Verify:

- Run focus setup on a clean temp state directory.
- Run focus setup on current state directory.

### T02: Update `focus` into roadmap mutation surface

Implement:

- Update `skills/focus/SKILL.md` around roadmap rows.
- Add deterministic helpers for status changes and row operations.
- Keep the existing focus-review behavior, but read from the new board.

Acceptance criteria:

- User can add, complete, drop, and reorder a row without manually editing
  markdown.
- Output remains human-scannable in under a minute.

### T03: Update `morning-sync` to validate and update roadmap

Implement:

- Validate focus statement.
- Warn on stale `Completed` rows.
- Pull candidate work from active projects, PR queue, and optionally issue
  tracker signals when available.
- Show added/skipped rows and update `last_sync`.

Acceptance criteria:

- Morning sync can run read-only or update mode.
- It does not create durable project state by itself.
- It surfaces PR/review queue without pretending unavailable data exists.

### T04: Simplify new `projects` scaffold defaults

Implement:

- Make project scaffolds shallow by default.
- Delay dependency graphs and verbose session blocks until real sequencing
  warrants them.
- Keep `execution.md` for PRs, pivots, effort, and follow-ups.

Acceptance criteria:

- New project setup creates a short, usable project file.
- Deep planning remains available when explicitly needed.

### T05: Compose `idea` artifacts

Implement:

- Replace `spec-handoff.md` with real idea-level `spec.md`.
- Extend idea storage to include optional `plan.md`.
- Update `idea brief`, `idea spec`, `idea plan`, and `idea promote` rules.
- Retire `/idea <slug> exec` as the primary mode name; keep it only as a
  compatibility alias to `spec` if needed.
- Ensure `idea plan` creates `plan.md` only for greenfield or pre-promotion
  execution shape, and routes to `spec-new-feature` when codebase grounding is
  required.
- Change `idea promote` so it adds/proposes a roadmap row first and creates a
  project only when durable execution memory is needed.

Acceptance criteria:

- One top-level `idea` skill owns the lifecycle.
- Idea folders can contain `idea.md`, `brief.md`, `spec.md`, and optional
  `plan.md`.
- `spec.md` contains high-level technical modules, design decisions, open
  technical questions, and effort summary; it is not `spec-new-feature/01_spec.md`.
- `plan.md` does not become an execution log.
- No separate `idea-brief`, `idea-spec`, `idea-plan`, or `idea-execute` skills
  are introduced.

### T06: Add execution-review drain contract for roadmap rows

Implement:

- Update daily review instructions and/or helper to read `roadmap.md`.
- Reconcile `Completed` rows with merged PRs and project execution memory.
- Drain completed rows into saved review history and relevant project execution
  memory when confirmed.

Acceptance criteria:

- Completed rows do not linger silently after day-end review.
- Ambiguous closures are surfaced instead of mutated blindly.

### T07: Merge agent instruction doc skills and hide rare maintenance surfaces

Implement:

- Merge `improve-agent-md` behavior into `create-agents-md`.
- Add create/improve/translate mode routing to `create-agents-md`.
- Preserve `improve-agent-md` as a temporary wrapper or remove it from default
  installation after compatibility review.
- Decide keep/fold/hide/cut for the remaining low-use skills.
- Prefer moving rare maintenance skills out of the default surface before
  deletion.

Initial recommendations:

- Keep: `projects`, `spec-new-feature`, `explain`, `wiki`, `review`, `focus`,
  `morning-sync`, `idea`, `execution-review`, `create-agents-md`.
- Fold or hide: `init-epic` behind `projects` for rare multi-repo bootstrap.
- Merge/remove: `improve-agent-md` into `create-agents-md`.
- Hide/maintenance: `compare`.

Acceptance criteria:

- Default skill surface is smaller by one agent-doc skill.
- `create-agents-md` can both create fresh files and improve existing
  `AGENTS.md` / `CLAUDE.md` files.
- Archived skills remain recoverable if useful.

### T08: Add skill composition contract

Implement:

- Add `skills/AGENTS.md` with the composition contract.
- Update `skills/README.md`, repo README, and runtime base instructions to point
  at the contract.
- Add `## Composes With` to retained skills and runtime wrappers.

Acceptance criteria:

- Every retained `SKILL.md` has a `## Composes With` section.
- The section names parent, children, format dependencies, state reads,
  write-through surfaces, handoffs, and return paths.

### T09: Run setup, smoke tests, and update docs

Implement:

- Run `~/.dot-agent/setup.sh`.
- Verify runtime copies under `~/.codex/skills`.
- Smoke test focus setup, morning sync readout, project setup, idea list, and
  execution-review render.
- Update README and `skills/README.md` with the new lifecycle.
