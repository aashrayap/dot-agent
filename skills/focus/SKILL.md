---
name: focus
description: >
  Mutate and inspect the daily roadmap/focus board. Use when the user wants to
  set focus, add or reorder roadmap rows, mark work complete, drop/park work,
  trim WIP, or decide whether a roadmap row should stay lightweight or move
  into deeper feature planning.
argument-hint: <optional current options / current problem / desired outcome>
disable-model-invocation: true
---

# Focus

## Composes With

- Parent: `morning-sync` for day-start orchestration.
- Children: `idea` when a row is still conceptual; `spec-new-feature` when a row needs deep planning; `excalidraw-diagram` when a roadmap change needs a durable visual; `morning-working-doc.py` for approved one-day focus packets.
- Uses format from: `excalidraw-diagram` for human-facing roadmap, workflow, or before/after visuals when useful.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md`.
- Writes through: `skills/focus/scripts/roadmap.py` for roadmap mutations and daily-review drainage; `skills/focus/scripts/morning-working-doc.py` for approved morning working docs.
- Hands off to: `morning-sync` for first morning call; `daily-review` for completed-row drainage; `spec-new-feature` for deep planning.
- Receives back from: `daily-review` when completed rows were drained or left ambiguous.

## Context

Run `~/.dot-agent/skills/focus/scripts/focus-setup.sh` first.

Deterministic helpers:

- `~/.dot-agent/skills/focus/scripts/roadmap.py`
- `~/.dot-agent/skills/focus/scripts/focus-update.py`
- `~/.dot-agent/skills/focus/scripts/focus-handoff.py`
- `~/.dot-agent/skills/focus/scripts/morning-working-doc.py`

Read `~/.dot-agent/state/collab/roadmap.md` every time. `focus.md` is a legacy
compatibility file, not the primary operating board. When the user wants help
deciding what should happen next, stay on the human roadmap by default. Do not
inspect legacy project/session state unless the user points to a specific
historical artifact.

This skill is the active control surface for:

- setting the daily focus statement
- adding, dropping, completing, or reordering roadmap rows
- reducing simultaneous work in progress
- parking lower-priority work without losing it
- routing focused work into `idea` or `spec-new-feature` when needed
- telling the user when to stay in `focus` versus switch to deep planning or
  implementation

`daily-review` closes the day. `execution-review` is forensic. Focus works in
the present.

When `morning-sync` proposes changes across multiple projects, do not bulk
apply them. Ask which stream should carry forward, then mutate only the
selected roadmap rows. Create a morning working doc only after explicit user
approval.

When a focus change is structural, such as reshaping the board, splitting
workstreams, or explaining why work moves between active/review/parked states,
lead with or link to an Excalidraw diagram. Use text-only output for small row
edits.

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

## Active Projects

| Project | Status | Task | Link | Notes |
|---------|--------|------|------|-------|
| <project or workstream> | In Progress | <plain-language task> | <PR/ticket/ref or -> | <short note> |
| <project or workstream> | Queued | <plain-language task> | <PR/ticket/ref or -> | <short note> |
| <project or workstream> | Completed | <plain-language task> | <PR/ticket/ref or -> | <short note> |

## Review Queue

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| <PR/review/blocker> | <repo/tool/user> | <status> | <short note> |

## Parked / Blocked

| Item | Reason | Revisit |
|------|--------|---------|
| <plain-language item> | <why parked or blocked> | <date/event or -> |
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
   - keep project/workstream names human-readable
   - avoid session IDs, dependency labels, and execution artifact anchors
3. Update `last_touched` on every write.
4. Keep the page concise. This is a control surface, not a diary.

When the resulting state is already obvious, prefer `roadmap.py` instead of
manual markdown editing.

### Create Morning Working Doc

Use this only after Ash approves carrying a selected focus stream forward.

1. Keep `roadmap.md` as the control plane.
2. Prefer one local working doc for the morning, not one doc per project:

```text
~/.dot-agent/state/collab/morning/YYYY-MM-DD.md
```

3. Write it with `skills/focus/scripts/morning-working-doc.py --write`.
4. Include only:
   - `Goal`
   - `Evidence`
   - `Important Docs`
   - `Next Step`
   - `Gate`
5. Link the working doc from the selected roadmap row only if it should remain
   visible beyond chat.

### Review What To Do Next

Use this when the user asks what they should work on now, what matters next, or wants a focus review.

1. Read legacy `focus.md` only if `roadmap.md` is missing or the user points to
   it explicitly.
2. Read `roadmap.md`.
3. Do not inspect legacy project/session state unless the user points to a specific historical artifact.
4. Treat this review as read-only. Do not rewrite `roadmap.md` unless the user explicitly asks.
5. Synthesize a decision summary with these exact headings:

```markdown
## Focus
- <plain-language current focus>

## Active Projects
- <project or workstream>: <high-level task>

## Review Queue
- <items that need review attention now, or "No tracked queue">

## Blocked / ignore
- <things that should wait, or are blocked by dependencies or missing decisions>

## Suggested Board Changes
- <add/move/complete/drop row, or "No changes">
```

6. Bias toward continuation over starting new work.
7. Call out contradictions inside `roadmap.md` when they matter.

### Decide The Next Control Surface

Use this whenever the user is moving from "what should I focus on?" toward "what task am I starting?".

- If the question is day-start triage or "what should I work on this morning?", use `morning-sync`.
- If the user does not yet have a coordination workspace for a multi-repo effort, use `init-epic` before feature planning.
- Stay in `focus` when the user is editing the roadmap, trimming WIP, parking items, or correcting the control surface.
- Use `daily-review` when the user wants to close the day, drain completed rows, or write a dated recap.
- Use `spec-new-feature` when a roadmap task needs deep planning or implementation artifacts.

### Deterministic vs Non-Deterministic

Treat these parts as deterministic:

- reading and writing `roadmap.md`
- enforcing `wip_limit`
- keeping completed rows available for `daily-review` drainage
- preserving the roadmap's human-readable schema

Treat these parts as non-deterministic judgment:

- choosing the best workstream when multiple active rows exist
- deciding whether to continue current momentum or start something new
- interpreting vague focus text that does not map cleanly to one active project/workstream row
- weighing contradictory roadmap rows against fresh user intent

### Route Into Deeper Planning

Use this when the user wants to turn a focus item into executable planning.

1. Run the setup script.
2. Keep or add a plain-language roadmap row for the workstream.
3. If the work is still conceptual, hand off to `idea`.
4. If the work needs code-grounded research, design, or tasks, hand off to `spec-new-feature`.
5. Present the resulting focus row and artifact path.

## Rules

- Use YYYY-MM-DD dates.
- Keep the file human-scannable in under a minute.
- Do not turn `roadmap.md` into a second project tracker.
- `roadmap.md` is the day-level control plane. Do not recreate hidden project/session state behind it.
- Do not bulk-apply multi-project morning suggestions. Mutate only selected streams.
- Do not create morning working docs during read-only review.
- Never emit `S01`, `S02`, session IDs, dependency graph labels, or `project.md#s01` anchors in normal human output.
- Do not expose `Available Sessions`, `Blocked Sessions`, Mermaid dependency graphs, or raw execution artifact internals in focus output.
- If the roadmap is missing a useful workstream/task row, suggest a plain-language board edit instead of reaching into hidden state.
