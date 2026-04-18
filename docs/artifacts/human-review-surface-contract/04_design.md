---
status: complete
feature: human-review-surface-contract
---

# Design: human-review-surface-contract

## Relevant Principles

- Human review starts from shape: diagrams first for non-trivial workflow,
  architecture, planning, review, and decision state.
- Markdown contracts carry precise rules, boundaries, exceptions, and file
  ownership.
- Code is sampled when contract layers cross into behavior or risk.
- Daily workflow and forensic session review are separate surfaces.
- Runtime portability matters, but day-to-day workflow can bias toward Codex.

## Decisions

- Root `AGENTS.md` stays short and runtime-portable; it names Codex preference
  but does not absorb detailed workflow policy.
- Root `README.md` describes repo architecture, setup/runtime, daily loop, and
  human review surfaces.
- `skills/AGENTS.md` remains generic skill authoring/setup/composition guidance;
  Excalidraw-specific policy does not live there.
- `skills/README.md` carries the human-facing skill model, visual-first
  presentation ladder, composability examples, and Excalidraw artifact contract.
- `excalidraw-diagram` owns diagram creation/rendering and pins the upstream
  renderer commit.
- `morning-sync` reads human roadmap rows by default.
- `focus` mutates the human roadmap and does not read project internals in the
  normal focus/review path.
- `daily-review` owns human closure, dated recaps, and completed-row drainage.
- `execution-review` owns forensic session review, typed session pipeline
  analysis, verification quality, response fit, skill leverage, and failure
  analysis.
- `projects` is durable execution memory used by explicit drill-down,
  migration, or promotion, not by the normal morning board.

## Open Risks

- Legacy gitignored state in other worktrees or machines may still contain
  `S01` rows until migrated.
- `focus/scripts/roadmap.py` now supports the new board shape, but broader
  helpers such as legacy `focus-update.py` still exist for compatibility.
- Visual-first output can become heavy if applied to tiny mechanical edits; the
  explicit exceptions should be preserved.
- The renderer is pinned, but it still relies on Playwright and an upstream
  template that loads Excalidraw from a CDN.

## File Map
