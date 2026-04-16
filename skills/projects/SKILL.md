---
name: projects
description: >
  Track durable project state from planning through delivery. Use when the user
  types "/projects" to view the portfolio, create or update a tracked project,
  choose the next execution slice, or hand off a live slice to
  /spec-new-feature. If the user first needs a new multi-repo coordination
  workspace, use init-epic.
argument-hint: <project-slug> [description]
disable-model-invocation: true
---

# Projects Skill

## Context

Run `~/.dot-agent/skills/projects/scripts/projects-setup.sh "$1"` first.

Deterministic helpers:

- `~/.dot-agent/skills/projects/scripts/update-execution.py`
- `~/.dot-agent/skills/projects/scripts/complete-session.py`

Read the project file, execution file, and AUDIT_LOG at the paths shown above to determine current state.

## Workflow Position

- `init-epic` bootstraps a new coordination workspace and repo map.
- `projects` owns durable milestones, live execution slices, and execution memory once that workspace exists.
- `focus` chooses which tracked project or slice gets attention now.
- `morning-sync` is the day-start readout on top of `focus` and active `projects`.

## Structure

**project.md** — active planning state: goal, scope, blockers, milestones, live execution slices, optional dependency graph, and completed work.

**execution.md** — durable execution memory: progress summary, PR ledger, pivots, effort summary, and open follow-ups. This is the home for what actually happened once execution began.

**AUDIT_LOG.md** — historical record of what changed and why.

Projects live under `~/.dot-agent/state/projects/` so both Claude and Codex on the same machine share the same state.

`project.md` remains the planning source of truth. `execution.md` records delivery reality. Technical details and codebase exploration are `/spec-new-feature`'s job. Prefer live delivery slices over speculative micro-steps.

## Key Concepts

**Milestones** — Leadership-facing progress markers ("We shipped auth"). They prove progression but do not dictate execution order.

**Sessions** — Delivery slices tackled via `/spec-new-feature` or direct execution. A session should be large enough to matter and small enough to produce a clear handoff, ref, or completion record. If it would not deserve its own Completed row, PR/ref, or audit entry, keep it out of `project.md`.

**Execution Memory** — The running ledger for what moved during delivery: current status, PRs, pivots, effort, and follow-ups.

## Routing

| MODE | Action |
|------|--------|
| `dashboard` | Show all projects listed by the script |
| `existing` | Read project state and execution memory. Use any additional user description to determine intent |
| `new` | Gather goal, scope, milestones, sessions, and dependencies. Write the planning docs and seed execution memory |

## Rules

- Use YYYY-MM-DD dates. Update `last_touched` on every doc change.
- Every change to `project.md` gets a dated `AUDIT_LOG.md` entry explaining what changed and why.
- Material changes to `execution.md` should also be reflected in `AUDIT_LOG.md` when they alter the project story: new PRs, pivots, scope changes, or major follow-ups. Routine metric refreshes do not need a standalone entry.
- Keep `project.md` and `execution.md` distinct: planning belongs in `project.md`; execution reality belongs in `execution.md`.
- Prefer one clear item in `## Available Sessions` when possible.
- Keep live slices short. Usually 1-4 total items across Available and Blocked is enough.
- Dependency graphs are optional. Use them only when there are 3+ live slices, real parallel work, or non-obvious sequencing risk.
- Do not create sessions just to read, inspect, brainstorm, or prepare. Put that detail in execution artifacts or the working session instead.
- If a stale speculative graph no longer matches delivery reality, collapse it into history instead of keeping two competing live plans.
- If the user is still choosing priorities, redirect to `focus`. If they first need a new coordination repo, redirect to `init-epic`.
- Use plain PR IDs or refs in the first column of the `PRs` table.
- Hyperlink external references when you cite them in narrative text. No bare URLs.
- Preserve the user's language.

### Execution Memory

Use `execution.md` to keep a project legible across long-running work:

- `## Progress Summary` should explain the current state in a few sentences, not a transcript.
- `## PRs` tracks real delivery artifacts and their state.
- `## Pivots & Changes` records scope or direction changes with a date and reason.
- `## Effort Summary` tracks simple metrics only when they are informative.
- `## Open Follow-ups` captures concrete loose ends that survived the latest session.

When reading an existing project, read `execution.md` whenever it exists. If it does not exist and the user is asking for execution-state updates, rerun setup as `projects-setup.sh --ensure-execution "$1"` before writing.

### Dependency Graphs (Optional)

Only add or maintain a dependency graph when it materially clarifies sequencing. If there is one live slice or a simple linear chain, skip the graph and let `## Available Sessions` and `## Blocked Sessions` carry the state.

When a graph exists:

- Remove completed sessions entirely: delete the node, edges, and style directive.
- Recalculate batch levels: sessions whose dependencies are all completed become batch 0.
- Use transitive reduction: only draw direct edges.
- Move newly unblocked sessions from `## Blocked Sessions` to `## Available Sessions`.

### Mermaid Format

Use `flowchart TB`. Force vertical ordering with invisible subgraphs by batch level:

```mermaid
flowchart TB
    subgraph b0[" "]
        direction LR
        s01([S01 Short name])
        s02([S02 Short name])
    end
    style b0 fill:none,stroke:none
```

Without subgraphs, Dagre pulls unblocked nodes down next to distant children. Node format: `sXX([SXX Name])` with names under 20 chars.

Color-code nodes by milestone using `style` directives. Match the emoji in the milestones table:

| Emoji | Fill | Stroke | Text |
|-------|------|--------|------|
| 🟦 | `#60a5fa` | `#1e40af` | `#1e3a5f` |
| 🟪 | `#c084fc` | `#6b21a8` | `#3b0764` |
| 🟧 | `#fb923c` | `#9a3412` | `#431407` |
| 🟩 | `#4ade80` | `#166534` | `#052e16` |
| 🟥 | `#f87171` | `#991b1b` | `#450a0a` |
| 🟨 | `#facc15` | `#854d0e` | `#422006` |

If more than 6 milestones exist, reuse colors.

<important if="MODE is new">

The setup script scaffolded `project.md`, `execution.md`, and `AUDIT_LOG.md`. Use any description from the user's invocation as intent. Ask clarifying questions only when you cannot safely infer goal, scope, or constraints. Then:

1. Define milestones as a table with emoji colors matching the graph node colors.
2. Identify blockers and constraints.
3. Break the work into delivery slices, not planning atoms.
4. Start with one current slice in `## Available Sessions` when possible, plus a small blocked/queued set.
5. Build a dependency graph only if there are 3+ live slices or non-obvious sequencing.
6. Write session details under `## Available Sessions` and `## Blocked Sessions` in this format:

   ```markdown
   #### <a id="sXX"></a>SXX — Name

   **Milestone:** 🟦 M1 — Name

   Brief description (no technical detail).

   **Blocked on:** [S01](#s01), [S02](#s02)
   ```

7. Write the `## Completed` table.
8. Seed `execution.md`:
   - write a `Progress Summary`
   - keep the tables ready for future updates
   - capture any obvious unresolved follow-ups

If the user only needs a new multi-repo coordination repo, use `init-epic` before creating project state here.

Iterate with the user, then write the docs and update the initial audit log entry if needed.

</important>

<important if="MODE is existing">

Read `project.md`, `AUDIT_LOG.md`, and `execution.md` when present, then determine intent from any additional description:

- **No description** → Present milestone progress, the best current available slice, the blocked slices that matter, and the latest execution readout.
- **Description provided** → Act accordingly: add, remove, reorder, merge, or complete sessions and milestones; update dependencies only when they matter; and update execution memory when the request changes what actually happened.
- If execution memory is missing and the user is asking for execution-state changes, ensure it explicitly before writing rather than treating ordinary reads as migration.
- If the user is still deciding today's priorities rather than changing durable project state, redirect to `focus`.

</important>

<important if="user wants to complete a session">

1. Apply Graph Maintenance rules.
2. Remove the session definition from Available or Blocked.
3. Add a row to the Completed table with session name, date, and PR/ref.
4. Update `execution.md` when relevant:
   - refresh `Progress Summary`
   - add or update `PRs`
   - record any `Pivots & Changes`
   - update `Effort Summary`
   - add surviving loose ends to `Open Follow-ups`
   Prefer `update-execution.py` for the deterministic row and metric updates when the state change is already known.
5. Log the completion in `AUDIT_LOG.md` with the session definition, completion date, refs, and outcomes.
6. Check whether this resolves a milestone and show which live slices are now available.

If completing the session makes sibling micro-sessions or an old speculative graph irrelevant, collapse them instead of preserving stale structure.

When the completion is structurally straightforward, use `complete-session.py`
first to remove the session block, append the Completed row, write the audit
entry, and update `execution.md` in the same deterministic path. Then do any
remaining milestone or dependency reasoning on top.

</important>

<important if="user wants to complete a milestone">

Verify all contributing sessions are resolved. Mark the milestone complete with a narrative summary. Update `execution.md` if the current project story changes. If no milestones remain, ask whether the whole project is complete (`status: complete`).

</important>

<important if="user wants to pick up a session or hand off to spec-new-feature">

The session must have no unfinished dependencies when a graph exists.

If there is exactly one clear available slice, recommend it directly instead of making the user re-choose among stale planning atoms.

Assemble a curated context block with:

- **Project Goal**
- **This Session**
- **What's Already Shipped**
- **Recent Execution Memory**
- **Blockers & Constraints**
- **Relevant Decisions**

Curate; do not dump the docs verbatim. Then ask whether to invoke `/spec-new-feature <session-slug>`.

If there is no durable slice yet because the user is still narrowing today's work, send them back to `focus`.

</important>
