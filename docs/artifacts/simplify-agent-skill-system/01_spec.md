---
status: draft
feature: simplify-agent-skill-system
---

# Feature Spec: simplify-agent-skill-system

## Goal

Simplify the dot-agent `AGENTS.md` surfaces and skill files so the harness is
easier to understand, compose, install, and maintain without losing Ash's
authored judgment or breaking daily Codex-first workflows.

The primary improvement target is the relationship between two contracts:

- `AGENTS.md` defines the human-agent communication protocol, operating loop,
  response expectations, and global safety norms.
- Skills define composable workflow modules: when to enter, what state to read,
  what artifacts to write, which skills they compose with, and how they hand
  work back.

The work should reduce duplicated instructions, unclear skill boundaries, and
hidden coupling between skills while preserving small useful pieces. Deletion is
secondary and should happen only after evidence, reversible migration, and
explicit approval.

## Users and Workflows

- Ash uses dot-agent as a personal agent harness across Codex and Claude Code,
  with Codex favored for day-to-day work.
- Codex and Claude read agent instructions, skills, state helpers, diagrams,
  and docs to perform planning, review, daily loops, and feature execution.
- Skills compose into larger workflows: daily loop, idea-to-PR, review and
  external gates, and docs/knowledge/visual artifacts.
- Ash sees value in small pieces across the system, especially
  `explain`/`compare`/`excalidraw-diagram`, but wants clearer grouping and
  contracts so they are easier to use together.
- Priority workflow cluster: `morning-sync`, roadmap/focus work, `focus`,
  `spec-new-feature`, `idea`, `handoff-research-pro`, and `review`.
- Future agents need enough context to resume work without rediscovering why a
  skill exists or why an instruction survived.
- Simplification work needs multiple human question rounds before reduction
  decisions so accidental deletion does not force Ash to recreate useful
  workflow memory.

## Acceptance Criteria

- Current `AGENTS.md` and skill surfaces are inventoried before any deletion or
  rewrite.
- Each skill is classified by evidence: active core workflow, composed child,
  occasional utility, improvement candidate, deprecated/quarantine candidate,
  or duplicate content.
- A clear `AGENTS.md` versus `SKILL.md` ownership model exists: global
  human-agent protocol in agent instructions; entry/exit/composition details in
  skills.
- A reusable skill composability contract exists or is adopted consistently
  enough that skills can declare parent/child relationships, handoffs, state
  inputs, artifact outputs, verification gates, and response responsibilities.
- Skill composition is documented as groups that match real workflows, including
  daily loop, idea/spec/review, external gates, and
  explain/compare/excalidraw.
- Duplicated instructions across root/project docs and installed skill copies
  are reduced to clear source-of-truth locations where possible.
- Any proposed deletion has a reversible path: quarantine, rename, redirect, or
  explicit deletion list with rationale.
- Important user-created knowledge is preserved or moved, not silently removed.
- The plan distinguishes content cleanup from runtime install/setup changes.
- Verification includes the narrowest useful setup, audit, or diff checks needed
  to prove the harness still installs and skills remain discoverable.

## Boundaries

- Do not delete skills, agent instructions, roadmap state, ideas, or handoff
  artifacts during planning.
- Do not optimize primarily for deletion; optimize first for clearer ownership,
  composition, grouping, and handoff behavior.
- Do not move global human-agent protocol into every skill.
- Do not move skill-specific workflow mechanics into global agent files unless
  they are truly universal.
- Do not patch installed runtime homes as the source of truth unless debugging
  setup drift.
- Do not collapse separate workflows merely because they share phrasing; only
  merge when ownership and usage evidence agree.
- Do not make Claude-only or Codex-only assumptions that reduce harness
  portability without an explicit decision.
- Do not treat the current workflow diagram as complete until research confirms
  the repo state.
- Browser QA is out of scope.

## Risks and Dependencies

- Useful rare skills may appear unused if only recent file references are
  checked.
- A too-thin `AGENTS.md` could lose the human-agent communication protocol that
  makes final responses, ledgers, visuals, gates, and follow-ups predictable.
- A too-heavy `AGENTS.md` could obscure skill-specific entry points and make
  skill behavior harder to compose.
- A vague skill composability contract could preserve files while still leaving
  agents confused about which skill owns which part of a workflow.
- Skill removal can break composition chains, automation prompts, roadmap rows,
  or external handoff conventions.
- Root `AGENTS.md`, project docs, skill README files, installed `.codex/skills`
  copies, and setup scripts may drift from each other.
- Some simplification options are value choices, not code facts; these require
  Ash's explicit answers before design.
- Runtime behavior may change over time, so the plan should avoid brittle local
  tricks and prefer portable source-of-truth cleanup.
