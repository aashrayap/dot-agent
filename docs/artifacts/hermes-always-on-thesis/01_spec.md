---
status: approved
feature: hermes-always-on-thesis
---

# Feature Spec: hermes-always-on-thesis

## Goal

Create a unified Hermes operating surface for the dot-agent harness:

- one centralized thesis that says what Hermes is watching for and why
- one daily document model Hermes can append to or summarize into
- default-on background behavior that runs without requiring a manual forensic review request
- clear boundaries so Hermes reports useful deltas without silently changing roadmap, focus, or project state

## Users and Workflows

- Ash starts the day and wants Hermes already watching the active thesis, recent work, gates, and contradictions.
- Ash or an agent needs a daily document that captures what Hermes saw without digging through raw execution evidence.
- Morning sync, daily review, and execution review need a shared Hermes source of truth instead of separate ad hoc summaries.
- A coding agent needs to know whether Hermes can write a finding, update a daily note, or only surface a recommendation.

## Acceptance Criteria

- A single Hermes operating document exists and defines the thesis, inputs, outputs, cadence, privacy rules, and mutation rules.
- Hermes is default-on in the approved workflow path, with a documented opt-out or pause path.
- Hermes writes or updates one daily working document per local day, or a clearly justified equivalent.
- The daily document distinguishes raw evidence intake, Hermes interpretation, gates, and human-approved actions.
- Morning sync and daily review can reference Hermes status without exposing raw session IDs, transcript anchors, dependency graph labels, or forensic internals.
- Hermes never mutates roadmap rows, focus text, parked/completed state, or working docs unless the workflow explicitly allows that mutation.
- A verification path proves the default-on behavior, daily document write path, and no-raw-internals rule.

## Boundaries

- Do not implement a daemon, scheduler, or automation until research confirms the existing harness-supported background mechanism.
- Do not make Hermes a planner that replaces `focus`, `morning-sync`, `daily-review`, or `execution-review`.
- Do not paste raw transcripts, private machine-local context, session IDs, or dependency graph internals into human-facing daily notes.
- Do not auto-promote inferred work into the roadmap.
- Do not design repo-specific stock workflow behavior here; `semi-stocks-2` remains a separate workstream.

## Human Direction

Initial Ash direction, captured 2026-04-21:

- `semi-stocks-2` PR #6 is merged.
- Explore a unified document for Hermes to operate on.
- Make Hermes always on by default and working in the background.
- Consider pasting or appending to a document per day.
- The feature needs a centralized thesis.

Direction update, captured 2026-04-21:

- Scope: `dot-agent` and `semi-stocks-2`, including work within those roots.
- Primary purpose: workflow awareness and non-forward-progress detection, especially repeated loops or going in circles.
- Daily document model: two documents. One appended log for intake, plus one curated synthesis/thesis document that can be further distilled for human presentation.
- Mutation posture: Hermes may suggest improvements and proposed actions, but the first version should stay simple.
- Product posture: keep the first slice simple.

Candidate thesis to validate:

> Hermes is an always-available background reviewer that compares recent execution evidence against a centralized thesis for the day, then writes concise, actionable deltas into a daily operating note.

Resolved human choices:

- Daily notes should split appended intake from curated synthesis.
- Default-on scope should cover `dot-agent` and `semi-stocks-2`.
- Suggestions are allowed, but implementation should start with a simple, low-permission slice.

Still open:

- Exact background mechanism and cadence.
- Exact schema for loop detection and daily synthesis.
- Whether suggestions should be plain text only or structured enough for later roadmap/focus mutation.

## Risks and Dependencies

- Existing Hermes state may already have a schema or reader contract that should not be bypassed.
- Background execution may depend on Codex heartbeat automation, shell hooks, runtime lifecycle hooks, or another local mechanism with different reliability and privacy tradeoffs.
- A daily document can become noisy if it mixes raw intake, interpretations, and proposed actions without strict sections.
- A centralized thesis can become stale if it is not tied to morning sync, current focus, or human-approved roadmap state.
- Always-on behavior can surprise Ash if opt-out, scope, and write permissions are not explicit.
