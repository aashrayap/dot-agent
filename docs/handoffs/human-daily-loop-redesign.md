# Human Daily Loop Redesign

Date: 2026-04-17

Status: live skill-contract handoff implemented for `morning-sync`, `focus`,
`daily-review`, and the roadmap helper. State migration remains future work.

## Decision

Move dot-agent's day-start and day-end workflow toward a human-readable daily
board, closer to Sushant's `dot-claude` model, while keeping dot-agent's richer
forensic review work out of the normal morning/focus path.

This handoff intentionally excludes `execution-review`; that work is being
handled in another session.

## Problem

`morning-sync` and `focus` currently expose project/session internals such as
`S01` and `S02` to the user:

```text
take S01 - Define shared Layer 10 schema contract
dot-agent-machinery S02/S03
```

That is not a human daily dashboard. It is execution planning metadata leaking
upward from `projects/*/project.md`.

The daily surface should answer:

- What am I focused on today?
- Which projects/workstreams are active?
- What are the high-level tasks?
- What needs review?
- What is parked or blocked?

It should not require the user to understand session IDs, dependency graphs, or
artifact internals.

## Target Model

```text
morning-sync / focus
└── human-readable roadmap.md
    ├── Focus
    ├── Active Projects
    │   ├── semi-stocks-2
    │   │   ├── Validate Wikiwise app workflow
    │   │   └── Capture breaks or missing affordances
    │   └── dot-agent
    │       └── Parked: simplify harness daily loop
    ├── Review Queue
    └── Parked / Blocked

daily-review
└── day-end closure, recap, and completed-row drain
```

`spec-new-feature` remains the place for deep implementation planning when a
task truly needs artifacts. Session IDs and dependency graphs, if they exist at
all, belong in deep execution artifacts or legacy project state, not in the
daily board.

## Scope

### 1. Retire `projects` From Normal Morning/Focus Loop

`morning-sync` and `focus` should stop depending on `projects/*/project.md` for
ordinary day-start output.

Allowed use:

- legacy read-only reference during migration
- explicit user request to inspect old project state
- one-time migration into human-readable roadmap rows

Not allowed in normal output:

- `S01`, `S02`, etc.
- `Available Sessions`
- `Blocked Sessions`
- Mermaid dependency graphs
- project anchors such as `project.md#s01`

### 2. Reshape `roadmap.md` Around Human Rows

The roadmap should become the daily control plane.

Recommended shape:

```markdown
---
last_sync: YYYY-MM-DD
last_touched: YYYY-MM-DD
---

# Roadmap

## Focus

<plain-language current intent>

## Active Projects

| Project | Status | Task | Link | Notes |
|---------|--------|------|------|-------|
| semi-stocks-2 | In Progress | Validate Wikiwise app workflow | - | Smoke test repo-owned export bundle in app |

## Review Queue

| Item | Source | Status | Notes |
|------|--------|--------|-------|

## Parked / Blocked

| Item | Reason | Revisit |
|------|--------|---------|
```

The exact table schema can change, but the key requirement is plain-language
project and task rows.

### 3. Rewrite `morning-sync` Around Roadmap Rows Only

`morning-sync` should read the human roadmap and return:

```markdown
## Focus
- <plain-language current focus>

## Active Projects
- <project>: <high-level task>

## Review Queue
- <PRs, blockers, or review items>

## Parked / Ignore
- <things that should not steal attention today>

## Suggested Board Changes
- <only if focus or rows are stale>
```

It can still use external signals later, such as GitHub PR queue or Linear, but
the baseline should not depend on `projects/*` state.

Implemented contract:

- `skills/morning-sync/SKILL.md` now reads `roadmap.md` by default.
- `projects/*` reads are allowed only for explicit legacy inspection, one-time
  migration, or user-requested deep execution drill-down.
- Human output uses `Focus`, `Active Projects`, `Review Queue`,
  `Blocked / Ignore`, and `Suggested Board Changes`.

### 4. Add Or Reshape `daily-review` As Human Closure Surface

Add a `daily-review` skill or reshape the existing closure workflow so it owns
day-end human recap and completed-row drainage.

Responsibilities:

- read `roadmap.md`
- collect completed rows
- gather closure signals where available, especially merged PRs
- ask about ambiguous closures
- write a dated human recap under `state/collab/daily-reviews/`
- drain completed rows from `roadmap.md`
- leave unfinished rows in place

This should be human-oriented, not forensic. It can cite `execution-review`
outputs later, but it should not become agent-quality review itself.

Implemented contract:

- `skills/daily-review/SKILL.md` owns human closure and completed-row drainage.
- `skills/daily-review/skill.toml` installs the skill for Codex.
- `daily-review` reads `roadmap.md` by default, writes dated recaps under
  `state/collab/daily-reviews/`, drains roadmap rows through `roadmap.py`, and
  does not read `projects/*` in the normal path.

### 5. Archive Or Freeze Existing `projects/*` State

Existing `state/projects/*` content is useful history but should not drive
morning output.

Options:

1. Move to `state/archive/projects-YYYYMMDD/`.
2. Keep in place but treat as legacy read-only.
3. Migrate selected active work into the new `roadmap.md` schema and archive the
   rest.

Recommended first step: keep legacy read-only until the new roadmap and
daily-review loop are stable, then archive.

## Non-Goals

- Do not modify `execution-review` in this workstream.
- Do not solve full project portfolio management.
- Do not preserve session IDs in human-facing output.
- Do not rebuild `spec-new-feature`.
- Do not add a heavier project database.

## Migration Notes

Current known bad examples:

- `state/collab/roadmap.md` has `S01 - Define shared Layer 10 schema contract`.
- `state/collab/focus.md` has `S01 - Define shared Layer 10 schema contract`.
- `state/projects/take/project.md` contains sessions, blocked sessions, and a
  dependency graph that should not appear in the daily loop.

Current user intent example:

```text
Focus: use and validate the new semi-stocks canonical repo + Wikiwise app workflow.

Project: semi-stocks-2
Tasks:
- Smoke-test Wikiwise against canonical/wiki-site export.
- Check search, previews, graph, and representative pages.
- Capture breaks or missing workflow affordances.
```

## Suggested Implementation Order

1. Add or update `daily-review` skill docs and helper skeleton. Done for skill
   docs; the existing `roadmap.py` helper now supports the new board shape.
2. Rewrite `morning-sync` to read only `roadmap.md` by default. Done in the
   live skill contract.
3. Simplify `focus` to mutate only the human roadmap. Done in the live skill
   contract.
4. Update `roadmap.py` schema helpers or replace them with a simpler table
   helper. Done for active projects, review queue, and parked/blocked tables.
5. Migrate current active focus into the new roadmap shape.
6. Mark `projects` as legacy/read-only in its skill docs, or remove it from the
   installed target list after migration.
7. Update root README and skills README diagrams/docs to match the new loop.
   Done in this batch.

## Acceptance Criteria

- Morning sync never emits `S01`, `S02`, session IDs, dependency graph labels, or
  `project.md#s01` anchors.
- Focus output is understandable without knowing dot-agent internals.
- Active work is grouped by project/workstream with plain-language task bullets.
- Daily review can drain completed rows into a dated recap.
- `projects/*` state is not read in the normal morning path.
- `execution-review` remains separate and untouched by this workstream.
