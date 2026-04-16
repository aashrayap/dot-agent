---
name: focus
description: >
  Mutate and inspect the daily roadmap/focus board. Use when the user wants to
  set focus, add or reorder roadmap rows, mark work complete, drop/park work,
  trim WIP, or decide whether a roadmap row should stay lightweight or promote
  into projects.
argument-hint: <optional current options / current problem / desired outcome>
disable-model-invocation: true
---

# Focus

## Composes With

- Parent: `morning-sync` for day-start orchestration.
- Children: `projects` when a roadmap row needs durable memory; `idea` when a row is still conceptual.
- Uses format from: none.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md`, legacy `focus.md`, and active projects when reviewing what to do next.
- Writes through: `skills/focus/scripts/roadmap.py` for roadmap mutations and `focus-promote.py` for project promotion.
- Hands off to: `morning-sync` for first morning call; `projects` for durable workstreams.
- Receives back from: `execution-review` when completed rows need draining or cleanup.

## Context

Run `~/.dot-agent/skills/focus/scripts/focus-setup.sh` first.

Deterministic helpers:

- `~/.dot-agent/skills/focus/scripts/roadmap.py`
- `~/.dot-agent/skills/focus/scripts/focus-update.py`
- `~/.dot-agent/skills/focus/scripts/focus-promote.py`
- `~/.dot-agent/skills/focus/scripts/focus-handoff.py`

Read `~/.dot-agent/state/collab/roadmap.md` every time. Keep
`~/.dot-agent/state/collab/focus.md` as a legacy compatibility file, not the
primary operating board. When the user wants help deciding what should happen
next, also read active project state from
`~/.dot-agent/state/projects/*/project.md` and `execution.md` when present.

This skill is the active control surface for:

- setting the daily focus statement
- adding, dropping, completing, or reordering roadmap rows
- reducing simultaneous work in progress
- parking lower-priority work without losing it
- promoting focused work into a tracked project when needed
- telling the user when to stay in `focus` versus switch to `projects`

Execution review looks backward. Focus works in the present.

## Storage

The canonical state file is:

```text
~/.dot-agent/state/collab/roadmap.md
```

If the file does not exist, the setup script creates it automatically and
migrates what it can from the legacy `focus.md`.

## Roadmap File Format

```markdown
---
last_sync: YYYY-MM-DD
last_touched: YYYY-MM-DD
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
```

## Modes

### Show Current Roadmap

Use this when the user invokes `/focus` with no clear update request.

1. Run the setup script.
2. Read `roadmap.md`.
3. Summarize:
   - focus statement
   - in-progress rows
   - queued rows
   - completed rows not yet drained
   - blocked or dropped rows
4. If the user is clearly asking what to do next, switch to the review behavior below instead of only echoing the file back.

### Update Roadmap

Use this when the user provides new notes, corrections, or asks to edit the page.

1. Read the full roadmap first.
2. Prefer section-aware edits:
   - keep `## Focus` short
   - keep `In Progress` rows few
   - keep project/workstream grouping stable
   - use `Queued` for deferred work
   - use `Completed` for work that should drain at day-end review
   - use `Dropped` only for abandoned work that should not drain as completed
3. Update `last_touched` on every write.
4. Keep the page concise. This is a control surface, not a diary.

When the resulting state is already obvious, prefer `roadmap.py` instead of
manual markdown editing.

### Review What To Do Next

Use this when the user asks what they should work on now, what matters next, or wants a focus review.

1. Read legacy `focus.md` only for compatibility context when it exists.
2. Read `roadmap.md`.
3. Read active and otherwise non-complete projects under `~/.dot-agent/state/projects/`.
4. Read each project's `execution.md` when it exists.
5. Run `focus-handoff.py` to determine whether the current focus already maps cleanly to a tracked project.
6. Treat this review as read-only. Do not rewrite `roadmap.md` unless the user explicitly asks.
7. Synthesize a decision summary with these exact headings:

```markdown
## Continue now
- <highest-leverage in-flight work>

## Worth starting
- <valuable unblocked work that is not the immediate best next step>

## Blocked / ignore
- <things that should wait, or are blocked by dependencies or missing decisions>

## Next control surface
- <stay in `focus`, or invoke `projects <slug>`, with a one-line why>
```

7. Bias toward continuation over starting new work.
8. Call out contradictions between `roadmap.md` and active project state when they matter.

### Decide The Next Control Surface

Use this whenever the user is moving from "what should I focus on?" toward "what task am I starting?".

- If the question is day-start triage or "what should I work on this morning?", use `morning-sync`.
- If the user does not yet have a coordination workspace for a multi-repo effort, use `init-epic` before trying to route into tracked project execution.
- Stay in `focus` when the user is editing the roadmap, trimming WIP, parking items, or correcting the control surface.
- Tell the user to invoke `projects <slug>` when all of these are true:
  - `focus-handoff.py` reports `PROJECT_READY=yes`
  - the user is transitioning from prioritization into execution
  - the next question is session/task level: what to start, what is unblocked, what changed, or what to hand off into `/spec-new-feature`
- If `focus-handoff.py` does not find a unique tracked project, keep the user in `focus` and explain what is still ambiguous.

### Deterministic vs Non-Deterministic

Treat these parts as deterministic:

- reading and writing `roadmap.md`
- enforcing `wip_limit`
- matching the current roadmap focus or active row to a tracked project slug with `focus-handoff.py`
- deciding that a clean project match means the next control surface is `projects <slug>` once the user moves into execution

Treat these parts as non-deterministic judgment:

- choosing the best workstream when multiple active projects exist
- deciding whether to continue current momentum or start something new
- interpreting vague focus text that does not map cleanly to one tracked project
- weighing contradictory planning state against more recent execution evidence

### Promote Into A Project

Use this when the user wants to turn a focus item into a tracked project.

1. Run the setup script.
2. Use `focus-promote.py --slug <slug> --why <reason>` to:
   - scaffold the project if it does not exist
   - ensure `execution.md` exists for an existing project before promotion writes
   - make it the current focus item without clearing unrelated parked work or blockers
3. Present the resulting focus and project paths.

## Rules

- Use YYYY-MM-DD dates.
- Keep the file human-scannable in under a minute.
- Do not turn `roadmap.md` into a second project tracker.
- `roadmap.md` is the day-level control plane. `projects/` remains the durable home for structured execution history.
- If project state suggests a better next move than the current focus page, say so plainly.
