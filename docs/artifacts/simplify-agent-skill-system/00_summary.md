---
status: draft
feature: simplify-agent-skill-system
---

# Simplify Agent Skill System

## Current State

Planning started from Ash's request to simplify dot-agent agent files and skill
files carefully, with multiple human question rounds before reduction decisions.
Ash clarified that the main optimization target is improvement, not deletion:
the system needs a stronger contract between `AGENTS.md` human-agent
communication protocol and skill-to-skill composability.

Implementation completed from `05_tasks.md`. No skills were deleted.

## Human Question Rounds

1. Human-agent communication protocol: what belongs globally in `AGENTS.md`
   versus locally in skills.
2. Skill composability contract: how skills declare parents, children, handoffs,
   artifacts, gates, and state ownership.
3. Workflow grouping: daily loop, idea-to-PR, review/handoff, and
   explain/compare/excalidraw.
4. Simplification policy: improve and group first; quarantine/delete only after
   evidence and explicit approval.
5. Execution order and verification gates.

## Guardrails

- Inventory before edits.
- Preserve user-authored judgment.
- Treat `AGENTS.md` as human-agent protocol, not a dumping ground for skill
  internals.
- Treat skills as composable workflow modules with explicit contracts.
- Prefer reversible cleanup.
- Improve grouping and source-of-truth clarity before deleting anything.
- Separate source-of-truth cleanup from installed runtime drift.
- Verify with setup, audit, or focused discovery commands before completion.

## Links

- `01_spec.md`
- `02_questions.md`
- `03_research.md`
- `04_design.md`
- `05_tasks.md`
