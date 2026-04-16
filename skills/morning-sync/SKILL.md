---
name: morning-sync
description: >
  Run the day-start operating loop across focus and active projects. Use when the
  user asks what to work on this morning, wants a daily sync, or wants a
  concise summary of what should happen next.
argument-hint: [notes]
disable-model-invocation: true
---

# Morning Sync

## Context

Run `~/.dot-agent/skills/morning-sync/scripts/morning-sync-setup.sh` first.

This skill is the day-start loop on top of the `focus` and `projects` layers. It should be opinionated and concise. The goal is not to restate every project; the goal is to help a human decide what deserves attention now.

Use `morning-sync` only after the underlying `focus` and `projects` state is current. It summarizes what those layers already know; it does not bootstrap a workspace or replace project planning. If the user still needs a coordination repo, use `init-epic` first.

## Inputs

Always read:

- `~/.dot-agent/state/collab/focus.md`
- active `~/.dot-agent/state/projects/*/project.md`
- active `~/.dot-agent/state/projects/*/execution.md` when present

If the user invocation includes fresh context for the day, incorporate it before making recommendations.

## Routine

### 1. Validate focus

- Confirm that `focus.md` exists and is in the canonical schema.
- Check whether the focus page looks stale relative to today.
- Check whether `## Now` aligns with active project state.
- Call out contradictions plainly.

### 2. Pull new work

- Review active projects for unblocked sessions, unresolved follow-ups, and fresh execution momentum.
- Prefer continuing something already in motion over starting a new track.
- Only pull in new work if:
  - the current focus is empty
  - the current in-flight work is blocked
  - another project has a clearly higher-leverage unblocked next step

### 3. Surface PR / review queue

- Read each project's `## PRs` table in `execution.md`.
- Surface items whose status suggests attention is needed now, such as:
  - `review`
  - `needs-review`
  - `waiting`
  - `follow-up`
  - `blocked`
- If no useful queue is recorded in execution memory, say so briefly instead of inventing one.

### 4. Recommend the day shape

Bias toward:

- one primary workstream
- at most one secondary pull-in
- explicit blocked or ignore items that should not steal attention

Treat this as read-only unless the user explicitly asks to update `focus.md`.

## Output Format

Use this exact structure:

```markdown
## Focus health
- <fresh or stale, with any contradiction worth calling out>

## Continue now
- <the best current path>

## Pull in next
- <optional secondary item worth starting or reviving>

## PR / review queue
- <items that need review attention now, or "No tracked queue">

## Blocked / ignore
- <things that should wait>

## Proposed focus
Focus: <one sentence>
In progress:
- <item>
Queued:
- <item>
```

Keep it short. If there is no good secondary item, say so instead of padding.

## Rules

- Do not silently rewrite `focus.md`.
- Prefer execution evidence over stale planning.
- Prefer current momentum over speculative new starts.
- Do not turn this into bootstrap work or project-plan creation; those belong to `init-epic`, `projects`, or `focus`.
- If all active work is blocked, say that directly and identify the unblock.
- If the project system lacks enough PR status detail to form a real review queue, say that the queue depends on better `execution.md` maintenance rather than pretending the data exists.
