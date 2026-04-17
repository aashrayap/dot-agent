---
status: complete
feature: human-review-surface-contract
---

# Feature Spec: human-review-surface-contract

## Goal

Define one contract for Ash's human review surfaces across the personal agent
harness:

- repo-level contract review through `AGENTS.md`, `README.md`, and diagrams
- skill authoring/runtime review through `skills/AGENTS.md`, `skills/README.md`,
  `skill.toml`, and each `SKILL.md`
- visual-first human presentation through Excalidraw diagrams for almost every
  skill that explains workflow, architecture, planning, review, or decisions
- Codex-session review through the actual transcript shape: user asks,
  assistant responses, tool calls, verification, PR summary, and follow-up fit
- Excalidraw as a callable visual documentation skill, not generic skill
  authoring guidance in `skills/AGENTS.md`

The contract should make it possible to move fast while giving a human a small,
predictable set of surfaces to inspect. Code remains available but should be
sampled or deeply reviewed only when risk triggers require it.

## Users and Workflows

- Ash reviews whether harness changes are understandable, portable, and aligned
  with current Codex-heavy usage.
- Codex implements or reviews changes and must know which artifacts to update
  when changing setup/runtime, skills, docs, diagrams, workflows, or session
  review behavior.
- Claude needs a minimal pointer into the same root agent instructions when
  runtime compatibility requires a Claude-readable entrypoint.
- Future agents should be able to inspect one Codex session and determine
  whether the agent followed the expected pipeline: scoped ask, skill use,
  evidence gathering, edits, verification, summary, and next decision.
- Human-presenting skills should lead with or point to a high-level drawing
  whenever the answer is explaining a workflow, contract, architecture, review
  model, decision tree, or proposed state. Text should deepen and specify the
  drawing rather than force the human to build the model from prose first.

## Visual-First Presentation Contract

For human-presenting skills, default to this ladder:

1. Excalidraw diagram or existing diagram link for the shape of the work.
2. Short prose summary that names the decision or proposed state.
3. Detailed text, tables, code references, or acceptance criteria for drill-down.

This applies strongly to skills such as `morning-sync`, `focus`,
`daily-review`, `execution-review`, `spec-new-feature`, `projects`, `idea`,
`compare`, `explain`, and `create-agents-md` whenever they present a model or
recommendation to Ash.

Exceptions:

- one-line status updates
- direct command output
- small mechanical edits
- narrow code-review findings where the exact line is the primary artifact
- transient progress messages during an active session

The durable rule is not "draw everything." It is: when the skill is presenting
understanding to a human, show the shape visually first and use text for depth.

## Acceptance Criteria

- The final contract distinguishes human-facing docs from agent-facing
  instructions.
- The final contract includes Codex session behavior as a review surface, not
  only repository files.
- The final contract names when Excalidraw belongs in the flow and where that
  guidance lives.
- Human-presenting skill outputs define Excalidraw as the default presentation
  layer for non-trivial workflow, architecture, planning, review, and decision
  explanations.
- The final contract defines when code review can be minimized and when code
  sampling or deep review is required.
- The final contract includes rapid-fire unresolved questions that can drive the
  next iteration.
- Any implementation task list identifies exact files and verification commands.

## Boundaries

- Do not make Excalidraw a generic requirement in `skills/AGENTS.md`.
- Do not bury the visual-first human presentation rule in agent-only docs; keep
  it in human-facing README/skill docs and in the callable
  `excalidraw-diagram` skill.
- Do not require a fresh diagram when an existing diagram already explains the
  current shape and can be linked.
- Do not hide code review for setup/runtime glue, renderers, adapters, or state
  mutation.
- Do not turn the daily human workflow into a project/session-ID dashboard.
- Do not rewrite the harness in this planning pass unless explicitly requested.
- Keep this feature lightweight: produce a contract and questions before broad
  code changes.

## Risks and Dependencies

- Runtime-specific entrypoints can drift from the root contract.
- README/AGENTS/diagram layers can look correct while `setup.sh`, `skill.toml`,
  or wrapper behavior is broken.
- Excalidraw diagrams can overstate architecture unless they show failure modes
  and review boundaries.
- Requiring diagrams too broadly can slow tiny tasks, so the contract needs an
  explicit exception for mechanical or line-level outputs.
- Codex session review is powerful but can become too transcript-heavy unless
  the expected response pipeline is typed.
- Existing untracked or local state may reflect prior experiments and should not
  be mixed into the contract without explicit selection.
