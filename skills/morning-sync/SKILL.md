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
- Children: `execution-review` evidence intake through its scripts, `focus` for selected roadmap mutations and approved working docs, `idea` for new concepts, `spec-new-feature` only after user chooses implementation, and `excalidraw-diagram` when the day shape needs a durable visual.
- Uses format from: `excalidraw-diagram` for human-facing workflow or before/after visuals when useful.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md`, recent Codex/Claude evidence through `scripts/recent-work-summary.py`, optional recent PR status, and optional Hermes findings.
- Writes through: `focus`/`roadmap.py` only when the user asks for an updating sync; approved morning working docs write through `focus/scripts/morning-working-doc.py`.
- Hands off to: `focus` for board edits; `idea` for incubation; `spec-new-feature` for deep implementation planning.
- Receives back from: `daily-review` through completed-row drainage history, `execution-review` through normalized evidence/history, and `focus` through roadmap state.

## Context

Run `~/.dot-agent/skills/morning-sync/scripts/morning-sync-setup.sh` first.

This skill is the first morning call. It runs on top of the human-readable
`roadmap.md` day board plus a lightweight recent-work intake from Codex/Claude
session evidence. It should be opinionated and concise. The goal is not to
restate every artifact; the goal is to help a human decide what deserves
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
- `~/.dot-agent/skills/morning-sync/scripts/recent-work-summary.py`

The recent-work helper may read Codex/Claude runtime evidence through the
`execution-review` adapters. It compresses this evidence into workstreams and
must not expose raw session ids, dependency graph labels, transcript anchors,
or forensic scores in normal morning output.

Use `--skip-prs` only for an explicit offline or fastest-path run. In normal
morning sync, let the helper attempt PR lookup and clearly distinguish skipped,
unavailable, empty, and present PR states.

If the user needs forensic historical context, hand off to `execution-review`
instead of expanding the morning packet.

If the user invocation includes fresh context for the day, incorporate it before making recommendations.

## Routine

### 1. Validate focus

- Confirm that `roadmap.md` exists and is in the canonical schema.
- Check whether the roadmap looks stale relative to today.
- Warn if it contains `Completed` rows that were not drained by `daily-review`.
- Check whether focus, active project rows, review queue, and parked/blocker rows are internally consistent.
- Call out contradictions plainly.

### 2. Pull recent work

- Run the recent-work helper and review `What you've been working on`.
- Weight local yesterday as primary, the 2 prior local days as secondary, and
  the 5 prior local days as tertiary context.
- Review `roadmap.md` active project rows for current tasks, unresolved follow-ups, and fresh human intent.
- Put inferred recent work that is not in the roadmap under `User Decides`.
- Do not auto-add inferred work to the roadmap.
- Prefer continuing something already in motion over starting a new track.
- Only pull in new work if:
  - the current focus is empty
  - the current in-flight work is blocked
  - another project has a clearly higher-leverage unblocked next step

### 3. Surface PR / review queue

- Read the `## Review Queue` section in `roadmap.md`.
- Let the recent-work helper check recent PRs where available. Present PR
  signal as a compact workstream summary: open count, recent merged count,
  closed-unmerged count when relevant, and one attention line for an open PR.
  Do not list every recent PR in the normal morning board.
- If the helper cannot reach GitHub but another current-session external signal
  is available, mention it as external PR signal rather than roadmap state.
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
For multi-project mornings, do not offer a single bulk apply. Ask which
workstream should carry forward. After the user selects, hand roadmap writes to
`focus` and create an approved working doc only when useful.

## Output Format

Use this exact structure:

```markdown
## Date
- <YYYY-MM-DD>

## Window
- Primary: yesterday
- Secondary: 2 prior days
- Tertiary: 5 prior days

## What you've been working on
| Workstream | Subcategory | Evidence | Last touched | State | Suggested next |
|---|---|---|---|---|---|

## User Decides
- <recent inferred work not on roadmap, or "No untracked recent work">

## Current commitments
- <roadmap commitments that still matter>

## Open gates
- <verification, blocked, rough edge, or review gates>

## Recent PRs
- <workstream>
  - <open count / recent merged count / attention line, or lookup state>

## Hermes
- Hermes: <no findings / count + short title>

## Recommended focus
- <one primary recommendation>

## Decision prompt
- Which stream should carry forward?

## Roadmap mutations proposed
- <only for a selected single stream, or "None until you select a stream">

## Not changing unless approved
- Roadmap rows, focus text, parked/completed status, and morning working docs.
```

Keep it short. If there is no good secondary item, say so instead of padding.

## Rules

- Do not silently rewrite `roadmap.md`.
- Do not create a morning working doc unless the user approves carrying a focus stream forward.
- Prefer execution evidence over stale planning.
- Prefer current momentum over speculative new starts.
- Do not turn this into bootstrap work or feature planning; those belong to `init-epic`, `spec-new-feature`, or `focus`.
- If all active work is blocked, say that directly and identify the unblock.
- Never emit `S01`, `S02`, session IDs, dependency graph labels, or `project.md#s01` anchors in normal human output.
- Do not expose `Available Sessions`, `Blocked Sessions`, Mermaid dependency graphs, or raw execution artifact internals in the morning board.
- Keep Hermes as a tiny status line. Deeper Hermes details belong in `execution-review`.
- Distinguish PR lookup states plainly: skipped by policy, unavailable,
  checked empty, or present summary.
- If the roadmap lacks enough PR status detail to form a real review queue, say that the board needs a review-row update rather than pretending the data exists.
