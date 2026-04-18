---
name: daily-review
description: >
  Close the human daily loop from the roadmap. Use when the user wants a
  day-end review, recap, completed-row drainage, or a human-readable record of
  what changed today.
argument-hint: [notes]
disable-model-invocation: true
---

# Daily Review

## Composes With

- Parent: user day-end review request, or `focus` when completed rows need drainage.
- Children: `focus` for roadmap edits, `morning-sync` for next-day handoff, `spec-new-feature` only when a recap exposes a real planning need, and `excalidraw-diagram` when closure needs a durable visual.
- Uses format from: `roadmap.md` human board rows; `excalidraw-diagram` for human-facing workflow or before/after closure visuals when useful.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md` by default; optional user-provided PR/review notes or external signals when available.
- Writes through: `skills/focus/scripts/roadmap.py review --write` for recap writes and completed-row drainage.
- Hands off to: `morning-sync` for the next day; `focus` for unresolved board cleanup.
- Receives back from: `morning-sync` and `focus` through roadmap state.

## Context

This skill owns human closure. It is not forensic agent-quality review and must
not replace `execution-review`.

Use `daily-review` when the user wants to close the day, summarize what
happened, drain completed rows from the roadmap, or leave a concise handoff for
tomorrow. The output should be understandable without knowing dot-agent
internals.

When closure involves multiple workstreams, review queues, or parked/blocked
movement that would be easier to understand visually, link an existing diagram
or create a small Excalidraw before/after map. Do not force a diagram for a
simple one-project recap.

## Inputs

Always read:

- `~/.dot-agent/state/collab/roadmap.md`

Optional inputs:

- fresh user notes from the current request
- PR, GitHub, Linear, or repo signals already available in the session
- explicit user-provided references to previous review or execution artifacts

Do not inspect legacy project/session state in the normal daily-review path.
Only read a historical artifact when the user explicitly points to it.

## Routine

### 1. Read The Human Board

- Identify the current `## Focus`.
- Collect `Completed` rows from `## Active Projects`.
- Inspect `## Review Queue` for items that changed, stayed open, or became stale.
- Inspect `## Parked / Blocked` for items that should remain parked tomorrow.

### 2. Resolve Closure

- Treat obvious completed rows as ready to drain.
- Ask before draining ambiguous rows.
- Leave unfinished rows in place.
- Do not infer deep execution status from session IDs, dependency graphs, or
  project artifacts.

### 3. Write The Recap

Write a dated recap through the deterministic helper:

```bash
~/.dot-agent/skills/focus/scripts/roadmap.py review --write --date YYYY-MM-DD
```

The helper writes:

```text
~/.dot-agent/state/collab/daily-reviews/YYYY-MM-DD.md
```

Use this shape:

```markdown
# Daily Review - YYYY-MM-DD

## Completed

- <project or workstream>: <plain-language completed task>

## Still Open

- <project or workstream>: <plain-language unfinished task>

## Review Queue

- <item needing review or "No tracked queue">

## Parked / Blocked

- <item and reason>

## Tomorrow Handoff

- <short next-day focus suggestion>
```

### 4. Drain Completed Rows

- Remove drained `Completed` rows from `roadmap.md` after they are recorded in
  the dated recap.
- Prefer `roadmap.py review --write --date YYYY-MM-DD`, which writes the recap
  and drains exact `Completed` rows in one pass.
- Use `roadmap.py drop --item <task>` only for targeted cleanup after the
  helper leaves an ambiguous row in place.
- Preserve unfinished, queued, parked, and blocked rows.
- Update `last_touched` on the roadmap when writing.
- If no completed rows can be drained, still write a recap when the user asks
  for day-end closure.

## Output Format

Use this exact structure:

```markdown
## Completed
- <drained item or "No completed rows drained">

## Still Open
- <unfinished item that remains on the board>

## Review Queue
- <review item or "No tracked queue">

## Parked / Blocked
- <parked or blocked item>

## Recap
- Wrote: <daily review path>

## Board Changes
- <rows drained / rows left / ambiguity needing user input>
```

## Rules

- Use YYYY-MM-DD dates.
- Keep the review human-oriented and concise.
- Never emit `S01`, `S02`, session IDs, dependency graph labels, or
  `project.md#s01` anchors in normal human output.
- Do not expose `Available Sessions`, `Blocked Sessions`, Mermaid dependency
  graphs, or raw execution artifact internals.
- Do not score Codex or Claude sessions. That belongs to `execution-review`.
- Do not run forensic review loops. Cite an existing review artifact only when
  the user explicitly provides it or asks for it.
- Ask before draining ambiguous completions.
