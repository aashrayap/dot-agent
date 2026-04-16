---
status: complete
feature: harness-flow-cleanup
---

# Research: harness-flow-cleanup

## Flagged Items

- Codex skill usage counts are based on explicit `/skill`, `$skill`, or `[$skill]`
  mentions in top-level Codex sessions. They undercount implicit trigger usage.
- Current session logs include recent migration discussion, so `spec-new-feature`
  and `explain` are somewhat inflated by this cleanup conversation.
- Several project entries are placeholders or backfills (`look`, `project`), which
  makes `projects` look heavier than the intended steady-state design.

## Findings

### F1: `focus` already writes the daily control file, but it is too sparse

Answer: `focus` owns `~/.dot-agent/state/collab/focus.md`, with `Current Focus`,
`Now`, `Next`, `Later / Parking Lot`, `Blockers`, and `Recent Shifts`.

Evidence:

- `skills/focus/SKILL.md`
- `state/collab/focus.md`

Confidence: high.

Open: whether to rename the file to `roadmap.md`, alias both paths, or keep
`focus.md` but change its schema.

### F2: Sushant's daily board is more useful for day execution

Answer: Sushant's `ROADMAP.md` has a focus statement plus project-grouped tables
with row statuses and links. Completed rows stay visible until day-end review
drains them.

Evidence:

- `/tmp/sushant-dot-claude.XDvZgZ/skills/roadmap/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/morning-sync/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/daily-review/SKILL.md`

Confidence: high.

Open: whether our board should include ticket-specific columns now, or generic
`Link` / `Spec` columns until Linear is wired.

### F3: `projects` is currently too deep for default daily steering

Answer: `projects` has milestones, session blocks, dependency graphs,
`execution.md`, and audit logs. That is useful for durable execution but too much
for ordinary "what should I do now?" flow.

Evidence:

- `skills/projects/SKILL.md`
- `state/projects/*/project.md`
- `state/projects/*/execution.md`

Confidence: high.

Open: how aggressively to simplify existing project docs versus only changing
new project scaffolds.

### F4: `idea` should compose Sushant's lifecycle as sub-artifacts, not top-level skills

Answer: Our current `idea` has concept, technical architecture, brief, spec
handoff, planning bridge, and promote. Sushant has separate `idea-brief`,
`idea-spec`, `idea-plan`, `idea-execute`, and `idea-effort`.

Evidence:

- `skills/idea/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/idea-brief/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/idea-spec/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/idea-plan/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/idea-execute/SKILL.md`
- `/tmp/sushant-dot-claude.XDvZgZ/skills/idea-effort/SKILL.md`

Confidence: high.

Decision direction: create real `spec.md` and optional `plan.md` files in each
idea folder. Replace the lighter `spec-handoff.md` concept.

### F5: Direct Codex usage is concentrated in a few skills

Answer: Across 89 top-level Codex sessions, explicit first-prompt usage appeared
for only four skills: `projects`, `spec-new-feature`, `explain`, and `wiki`.

Evidence from local Codex logs:

| Skill | First-prompt sessions | Any-session mentions | Mentions | Last seen |
|---|---:|---:|---:|---|
| projects | 5 | 7 | 9 | 2026-04-15 |
| spec-new-feature | 2 | 6 | 6 | 2026-04-16 |
| explain | 2 | 4 | 4 | 2026-04-16 |
| wiki | 2 | 4 | 4 | 2026-04-09 |
| review | 0 | 2 | 2 | 2026-04-07 |
| compare | 0 | 0 | 0 | none |
| create-agents-md | 0 | 0 | 0 | none |
| execution-review | 0 | 0 | 0 | none |
| focus | 0 | 0 | 0 | none |
| idea | 0 | 0 | 0 | none |
| improve-agent-md | 0 | 0 | 0 | none |
| init-epic | 0 | 0 | 0 | none |
| morning-sync | 0 | 0 | 0 | none |

Confidence: medium. The direction is useful, but implicit triggers and recent
new skills are undercounted.

Open: whether to measure Claude usage too before cutting shared skills.

## Patterns Found

- Lightweight daily state should be row-based, not graph-based.
- Durable execution state should live in promoted project directories.
- Completed daily rows should be drained by day-end review, not deleted during
  the day.
- One composed skill with modes is preferable to many tiny lifecycle skills when
  the state owner is the same.
- Usage count alone is insufficient. Classify each skill by both frequency and
  layer: strategic, tactical, disposable.

## Core Docs Summary

- `focus` is the current day-level control plane, but its schema is closer to a
  small focus note than a working roadmap.
- `morning-sync` already sits on top of `focus` and `projects`, but it is
  read-only and cannot yet ingest/update a roadmap-like board.
- `projects` is the right place for durable execution memory, but not the right
  default surface for every current task.
- `idea` should keep product-first concept shaping while adding explicit
  composed artifacts for brief/spec/plan.
- Sushant's workflow is stronger as a daily operating loop; ours is stronger as
  a shared-state, multi-runtime harness.

## Open Questions

- Should the canonical file be `roadmap.md` with a migration from `focus.md`, or
  should `focus.md` keep its path and adopt the roadmap schema?
- Should `idea plan` create a real `plan.md`, or only route into
  `spec-new-feature`?
- Should rare maintenance skills be removed from `skills/`, moved under a
  maintenance plugin, or left installed but de-emphasized in descriptions?
- `improve-agent-md` and `create-agents-md` overlap enough to merge. Keep the
  `create-agents-md` capability, broaden it to create/improve/translate modes,
  and retire `improve-agent-md` as a separate default surface after compatibility
  review.
- Should cut decisions wait for Claude usage counts too?
