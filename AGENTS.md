# dot-agent Instructions

This repo is Ash's personal agent harness for Claude Code and Codex. Codex is
the preferred day-to-day runtime; keep the harness portable unless Ash asks for
a runtime-specific choice.

`~/.dot-agent` is source of truth. Runtime homes such as `~/.codex` and
`~/.claude` are install targets. Do not put private context, risky local
permission bypasses, or one-off machine overrides in tracked config.

## Operating Loop

- Read only the layer needed for the task. Keep root context small and pull
  deeper harness facts through the references below.
- Prefer Codex-first ergonomics, durable planning quality, and portable setup
  behavior in that order.
- Preserve existing user or concurrent changes. Do not revert unrelated dirty
  files.
- For non-trivial implementation, inspect current code/docs first, make scoped
  edits, run focused verification, then report what changed and what remains.
- Treat chat as the receipt unless state must survive into roadmap rows, PRs,
  docs, reviews, or handoff artifacts.
- When plans/specs already exist, compare them against current main before
  executing. Fix stale paths, renamed skills, and source/runtime contradictions
  as part of the same delivery.

## Human Response Contract

For non-trivial work, final responses use:

```text
This Session Focus
Result
Next Actions
```

`This Session Focus` is the first slot: 1-2 short lines for why this session
started and current state. `Result` carries the receipt: changes, verification,
open risks, and useful links or visuals. Add `Ledger` only when state could
disappear: multiple requests, corrections, parked items, or handoff-heavy work.
`Next Actions` should be concrete and, when direction is needed, answerable by
number or short phrase.

Before final response, map the latest user requests to done, not done, or
parked. If a request is incomplete, say that plainly.

## Review

For reviews, lead with concrete findings, severity, and file paths. Prioritize
behavioral regressions, instruction drift, missing verification, and
contradictions between Claude and Codex surfaces. Keep summaries secondary.

## Read When Needed

- Harness layout, setup, runtime install targets, and skill packaging:
  `~/.dot-agent/docs/harness-runtime-reference.md`
- Skill authoring policy:
  `~/.dot-agent/skills/AGENTS.md`
- Skill catalog, install model, and workflow diagrams:
  `~/.dot-agent/skills/README.md`
- Machine-local roadmap, ideas, reviews, and caches:
  `~/.dot-agent/state/` through owning skills or helper scripts.
