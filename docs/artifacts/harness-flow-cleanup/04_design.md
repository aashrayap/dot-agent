---
status: draft
feature: harness-flow-cleanup
---

# Design: Harness Flow Cleanup

## Relevant Principles

- Shared source lives in `~/.dot-agent`; mutable state belongs under
  `~/.dot-agent/state`.
- Strategic layer should compound: idea quality, judgment, durable project
  memory, review loops.
- Tactical helpers should reduce repeated agent reasoning, not create more
  first-class choices.
- Disposable runtime-specific command details should not shape the shared
  harness.
- Daily state should be fast to scan and cheap to edit.

## Decisions

### D1: Promote the daily board concept

Create a canonical daily board with Sushant's ROADMAP shape, but under shared
state:

```text
~/.dot-agent/state/collab/roadmap.md
```

Recommended schema:

```markdown
---
last_sync: YYYY-MM-DD
---

# Roadmap

## Focus
<one or two sentences>

## <Project or Workstream>
| Status | Item | Link | Spec / Idea / Project | Notes |
|--------|------|------|-----------------------|-------|
| In Progress | <title> | <PR/ticket/ref or -> | <link or -> | <short note> |
| Queued | <title> | <PR/ticket/ref or -> | <link or -> | <short note> |
| Completed | <title> | <PR/ticket/ref or -> | <link or -> | <short note> |

## Uncategorized
| Status | Item | Link | Spec / Idea / Project | Notes |
|--------|------|------|-----------------------|-------|
```

Compatibility:

- Keep reading existing `focus.md` during migration.
- Either make `focus.md` a symlink/compat wrapper, or have `focus` setup create
  `roadmap.md` and print both paths for one release.

### D2: Make `focus` the roadmap mutation surface

Do not add a new top-level `roadmap` skill yet. Update `focus` so it can:

- view the board
- add/edit/reorder/drop rows
- change statuses
- update the focus statement
- preserve project grouping

This keeps one daily-control skill while borrowing Sushant's stronger board.

### D3: Make `morning-sync` the board renderer and ingester

Lean `morning-sync` toward Sushant's flow:

- validate focus
- warn if `Completed` rows were not drained
- propose new rows from active projects, PRs, and optionally issue trackers
- surface skipped items and why
- surface PR/review queue globally when `gh` is available
- update `last_sync`

It should write the roadmap only when the user asks for sync/update behavior or
when its mode explicitly says it will update the board.

### D4: Make `projects` shallower by default

Keep `projects` as durable state, but stop making deep milestone/session graphs
the default experience.

New project scaffolds should prefer:

- short goal
- current roadmap rows or available items
- completed rows
- execution memory

Only add milestones, dependency graphs, and detailed session blocks when:

- there are 3+ real work slices
- sequencing is non-obvious
- the project needs a handoff into `spec-new-feature`
- the user explicitly asks for durable project planning

This makes projects feel more like Sushant's project-grouped roadmap until depth
is warranted.

### D5: Make `idea` a composed lifecycle skill

Keep one top-level `idea` skill, but adopt Sushant's artifact ladder more fully.
The first migration left `spec-handoff.md`; replace that with real idea-level
`spec.md` and optional `plan.md`.

```text
~/.dot-agent/state/ideas/<slug>/
  idea.md       # concept, raw log, product frame
  brief.md      # leadership/product pitch
  spec.md       # high-level technical spec, no code tasking
  plan.md       # optional execution-shape plan or pointer into spec-new-feature
```

Modes:

- `/idea <slug>`: concept refinement
- `/idea <slug> brief`: product brief
- `/idea <slug> spec`: high-level technical spec
- `/idea <slug> plan`: create `plan.md` only for greenfield or pre-promotion
  execution shape; route existing-codebase work into `spec-new-feature`
- `/idea <slug> promote`: add roadmap row first; create project only when durable
  execution memory is needed

Naming:

- Retire `/idea <slug> exec` as the primary mode name because it means
  architecture, not execution.
- Keep `exec` as a compatibility alias to `/idea <slug> spec` for one release if
  needed.

Promotion threshold:

- Default promotion writes or proposes a `roadmap.md` row.
- Create a project only when the idea needs milestones, PR/pivot tracking,
  multi-session memory, cross-repo coordination, or explicit durable follow-ups.
- Durable execution truth still belongs in `projects/execution.md`; do not port
  Sushant's `idea-execute` log into the idea folder.

### D6: Keep `spec-new-feature` as the deep implementation workflow

`spec-new-feature` remains the code-grounded artifact workflow. It should consume
idea `spec.md` or `plan.md`, but it should not be the default daily planning
surface. It should be invoked when repo/codebase grounding is required.

### D7: Cut by role, not only by count

Usage-based classification:

| Skill | Direct Codex usage | Role | Decision |
|---|---:|---|---|
| projects | high | durable execution | keep, simplify default shape |
| spec-new-feature | medium | deep implementation | keep |
| explain | medium | explanation | keep |
| wiki | medium | knowledge system | keep |
| review | low explicit | code review | keep |
| focus | zero explicit, newly introduced | daily board | keep, redesign into roadmap |
| morning-sync | zero explicit, newly introduced | day-start loop | keep, strengthen |
| idea | zero explicit, strategically important | incubation | keep, compose artifacts |
| execution-review | zero explicit, newly introduced | day/week review | keep |
| init-epic | zero explicit, rare | multi-repo bootstrap | fold behind projects/init if possible |
| compare | zero explicit but requested now | diagnostic utility | hide or keep as maintenance |
| create-agents-md | zero explicit | agent instruction docs | keep as merged create/improve surface |
| improve-agent-md | zero explicit | agent instruction docs | merge into create-agents-md, then remove or leave legacy alias |

### D8: Merge `improve-agent-md` into `create-agents-md`

The two skills have the same underlying job: maintain repo/runtime agent
instruction markdown.

Merge them into one capability with modes:

- **create**: generate a fresh Codex-native `AGENTS.md` when an existing file is
  absent, obsolete, or explicitly not worth salvaging.
- **improve**: rewrite an existing `AGENTS.md` or `CLAUDE.md` in place while
  preserving accurate commands, paths, and repo conventions.
- **translate**: keep paired Claude and Codex instruction files factually aligned
  while translating runtime-specific structure.

Recommended implementation:

- Keep `create-agents-md` as the user-visible skill for now, because it already
  exists and is Codex-specific.
- Broaden its description to "create or improve agent instruction markdown."
- Copy the useful target-selection, Claude/Codex target rules, and final checks
  from `improve-agent-md`.
- Leave `improve-agent-md` as a short legacy wrapper for one release, or remove it
  from default installation after confirming no Claude-side workflow depends on
  it.

### D9: Require `Composes With` on retained skills

Every retained skill should declare its composition contract:

```markdown
## Composes With

- Parent:
- Children:
- Uses format from:
- Reads state from:
- Writes through:
- Hands off to:
- Receives back from:
```

This section makes "skills within skills" explicit without creating more
top-level commands. It distinguishes format reuse (`compare` uses `explain`),
routing (`morning-sync` routes to `focus`/`projects`), ownership handoff
(`idea` hands off to `spec-new-feature`), read-only state access, write-through
mutation, and returned execution reality.

## Open Risks

- Renaming `focus.md` to `roadmap.md` may break existing helper scripts unless
  compatibility is explicit.
- Making `projects` shallower could lose useful execution discipline if the
  promotion threshold is too low.
- Adding `idea spec` and `idea plan` artifacts may recreate Sushant's many-stage
  complexity unless the top-level skill remains one composed surface.
- Cutting maintenance skills too aggressively may remove useful rare workflows.
- Keeping the merged skill under the `create-agents-md` name may be slightly
  misleading for improve-only requests, but it avoids adding another top-level
  skill name.
- Over-specifying composition could become boilerplate. Keep entries concrete
  and short, with real skill/state/helper names.

## File Map

Likely changes:

- `skills/focus/SKILL.md`
- `skills/focus/scripts/focus-setup.sh`
- `skills/focus/scripts/focus-update.py`
- new `skills/focus/scripts/roadmap-*.py` helpers or renamed helpers
- `skills/morning-sync/SKILL.md`
- `skills/morning-sync/scripts/morning-sync-setup.sh`
- `skills/projects/SKILL.md`
- `skills/projects/scripts/projects-setup.sh`
- `skills/idea/SKILL.md`
- possible new `skills/idea/scripts/idea-*.py` helpers
- `skills/execution-review/SKILL.md`
- `skills/create-agents-md/codex/SKILL.md`
- `skills/create-agents-md/skill.toml`
- `skills/improve-agent-md/SKILL.md`
- `skills/improve-agent-md/skill.toml`
- `skills/README.md`
- `skills/AGENTS.md`
- `README.md`
- `setup.sh` cleanup list if skills are archived or moved
