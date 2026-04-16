---
name: focus
description: >
  Active work narrowing and focus control.
  Use when the user wants to choose one workstream, trim WIP, park ideas,
  decide what deserves attention now versus later, or determine whether to
  stay in focus mode versus switch into project execution.
argument-hint: <optional current options / current problem / desired outcome>
disable-model-invocation: true
---

# Focus

## Context

Run `~/.dot-agent/skills/focus/scripts/focus-setup.sh` first.

Deterministic helpers:

- `~/.dot-agent/skills/focus/scripts/focus-update.py`
- `~/.dot-agent/skills/focus/scripts/focus-promote.py`
- `~/.dot-agent/skills/focus/scripts/focus-handoff.py`

Read `~/.dot-agent/state/collab/focus.md` every time. When the user wants help
deciding what should happen next, also read active project state from
`~/.dot-agent/state/projects/*/project.md` and `execution.md` when present.

This skill is the active control surface for:

- choosing one current focus
- reducing simultaneous work in progress
- parking lower-priority work without losing it
- promoting focused work into a tracked project when needed
- telling the user when to stay in `focus` versus switch to `projects`

Execution review looks backward. Focus works in the present.

## Storage

The canonical state file is:

```text
~/.dot-agent/state/collab/focus.md
```

If the file does not exist, the setup script creates it automatically.

## Focus File Format

```markdown
---
status: active
started: YYYY-MM-DD
last_touched: YYYY-MM-DD
wip_limit: 1
---

# Focus

## Current Focus

<one short line>

## Now

- item

## Next

- item

## Later / Parking Lot

- item

## Blockers

- blocker

## Recent Shifts

| Date | From | To | Why |
|------|------|----|-----|
```

## Modes

### Show Current Focus

Use this when the user invokes `/focus` with no clear update request.

1. Run the setup script.
2. Read `focus.md`.
3. Summarize:
   - current focus
   - what is active now
   - what is queued next
   - what is parked
   - blockers
4. If the user is clearly asking what to do next, switch to the review behavior below instead of only echoing the file back.

### Update Focus

Use this when the user provides new notes, corrections, or asks to edit the page.

1. Read the full file first.
2. Prefer section-aware edits:
   - keep `## Current Focus` short
   - keep `## Now` to the single active item when possible
   - keep `## Next` short
   - use `## Later / Parking Lot` for deferred work
   - track blockers explicitly
3. Update `last_touched` on every write.
4. Keep the page concise. This is a control surface, not a diary.

When the resulting state is already obvious, prefer `focus-update.py set ...`
instead of manual markdown editing.

Unspecified list sections should be preserved. Only pass `--now`, `--next`,
`--later`, or `--blocker` when you intend to replace that section.

### Review What To Do Next

Use this when the user asks what they should work on now, what matters next, or wants a focus review.

1. Read `focus.md`.
2. Read active and otherwise non-complete projects under `~/.dot-agent/state/projects/`.
3. Read each project's `execution.md` when it exists.
4. Run `focus-handoff.py` to determine whether the current focus already maps cleanly to a tracked project.
5. Treat this review as read-only. Do not rewrite `focus.md` unless the user explicitly asks.
6. Synthesize a decision summary with these exact headings:

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
8. Call out contradictions between `focus.md` and active project state when they matter.

### Decide The Next Control Surface

Use this whenever the user is moving from "what should I focus on?" toward "what task am I starting?".

- If the question is day-start triage across active projects, use `morning-sync`.
- If the user does not yet have a coordination workspace for a multi-repo effort, use `init-epic` before trying to route into tracked project execution.
- Stay in `focus` when the user is still choosing a workstream, trimming WIP, parking items, or correcting the control surface.
- Tell the user to invoke `projects <slug>` when all of these are true:
  - `focus-handoff.py` reports `PROJECT_READY=yes`
  - the user is transitioning from prioritization into execution
  - the next question is session/task level: what to start, what is unblocked, what changed, or what to hand off into `/spec-new-feature`
- If `focus-handoff.py` does not find a unique tracked project, keep the user in `focus` and explain what is still ambiguous.

### Deterministic vs Non-Deterministic

Treat these parts as deterministic:

- reading and writing `focus.md`
- enforcing `wip_limit`
- matching the current focus or active `Now` item to a tracked project slug with `focus-handoff.py`
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
- Do not turn `focus.md` into a second project tracker.
- `focus.md` is the day-level control plane. `projects/` remains the durable home for structured execution history.
- If project state suggests a better next move than the current focus page, say so plainly.
