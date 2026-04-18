---
name: morning-sync
description: >
  Run the day-start operating loop from the human roadmap. Use when the user
  asks what to work on this morning, wants a daily sync, or wants a concise
  summary of what should happen next.
argument-hint: [notes]
disable-model-invocation: true
---

# Morning Sync

## Composes With

- Parent: first morning call from the user.
- Children: `focus` for roadmap mutations, `idea` for new concepts, `spec-new-feature` only after user chooses implementation, and `excalidraw-diagram` when the day shape needs a durable visual.
- Uses format from: `excalidraw-diagram` for human-facing workflow or before/after visuals when useful.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md` by default; optional external PR/review queues when available.
- Writes through: `focus`/`roadmap.py` only when the user asks for an updating sync.
- Hands off to: `focus` for board edits; `idea` for incubation; `spec-new-feature` for deep implementation planning.
- Receives back from: `daily-review` through completed-row drainage history.

## Context

Run `~/.dot-agent/skills/morning-sync/scripts/morning-sync-setup.sh` first.

This skill is the first morning call. It runs on top of the human-readable
`roadmap.md` day board. It should be opinionated and concise. The goal is not
to restate every artifact; the goal is to help a human decide what deserves
attention now.

Use `morning-sync` when the user asks what to work on this morning, wants a
daily sync, or wants to start the day. It summarizes the daily board's focus,
active projects, review queue, and parked/blocker rows. It does not replace
feature planning. If the user still needs a coordination repo, use `init-epic`
first.

When the sync is explaining a non-trivial workflow shift, multi-workstream
board, or before/after change, point to an existing diagram or create a small
Excalidraw view. For a normal short daily sync, bullets are enough.

## Inputs

Always read:

- `~/.dot-agent/state/collab/roadmap.md`

Do not inspect gitignored legacy project/session state during the normal
morning path. If the user needs historical context, ask for the explicit file
or artifact they want reviewed.

If the user invocation includes fresh context for the day, incorporate it before making recommendations.

## Routine

### 1. Validate focus

- Confirm that `roadmap.md` exists and is in the canonical schema.
- Check whether the roadmap looks stale relative to today.
- Warn if it contains `Completed` rows that were not drained by `daily-review`.
- Check whether focus, active project rows, review queue, and parked/blocker rows are internally consistent.
- Call out contradictions plainly.

### 2. Pull new work

- Review `roadmap.md` active project rows for current tasks, unresolved follow-ups, and fresh human intent.
- Prefer continuing something already in motion over starting a new track.
- Only pull in new work if:
  - the current focus is empty
  - the current in-flight work is blocked
  - another project has a clearly higher-leverage unblocked next step

### 3. Surface PR / review queue

- Read the `## Review Queue` section in `roadmap.md`.
- Surface rows whose status suggests attention is needed now, such as:
  - `review`
  - `needs-review`
  - `waiting`
  - `follow-up`
  - `blocked`
- If optional external GitHub or Linear signals are available in the current session, mention them as external signals rather than treating them as roadmap state.
- If no useful queue is recorded, say so briefly instead of inventing one.

### 4. Recommend the day shape

Bias toward:

- one primary workstream
- at most one secondary pull-in
- explicit blocked or ignore items that should not steal attention

Treat this as read-only unless the user explicitly asks to update `roadmap.md`.

## Output Format

Use this exact structure:

```markdown
## Focus
- <plain-language current focus>

## Active Projects
- <project or workstream>: <high-level task>

## Review Queue
- <items that need review attention now, or "No tracked queue">

## Blocked / ignore
- <things that should wait>

## Suggested Board Changes
- <add/move/complete/drop row, or "No changes">
```

Keep it short. If there is no good secondary item, say so instead of padding.

## Rules

- Do not silently rewrite `roadmap.md`.
- Prefer execution evidence over stale planning.
- Prefer current momentum over speculative new starts.
- Do not turn this into bootstrap work or feature planning; those belong to `init-epic`, `spec-new-feature`, or `focus`.
- If all active work is blocked, say that directly and identify the unblock.
- Never emit `S01`, `S02`, session IDs, dependency graph labels, or `project.md#s01` anchors in normal human output.
- Do not expose `Available Sessions`, `Blocked Sessions`, Mermaid dependency graphs, or raw execution artifact internals in the morning board.
- If the roadmap lacks enough PR status detail to form a real review queue, say that the board needs a review-row update rather than pretending the data exists.
