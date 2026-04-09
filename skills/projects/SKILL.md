---
name: projects
description: >
  Track multi-milestone projects as a dependency-graph TODO list.
  Use when the user types "/projects" to view the portfolio, create a project,
  or report progress (scope changes, completed sessions, merged PRs).
argument-hint: <project-slug> <new|update> [details...]
disable-model-invocation: true
---

# Projects Skill

A glorified TODO list with a dependency-graph visualization. This skill owns _what_, _when_, and _what's blocking_ — nothing else. Implementation work happens outside; results get reported back here so milestones, sessions, and priorities stay current.

Every change is logged so the project's evolution is traceable end to end.

## Context

!`~/.claude/skills/projects/scripts/projects-setup.sh "$0" "$1"`

Read the project file and AUDIT_LOG at the paths shown above to determine current state.

## Files

- **project.md** — live state: goal, scope, milestones, dependency graph, sessions list, completed table
- **AUDIT_LOG.md** — append-only history: every change with date + rationale

## Key Concepts

**Milestones** (`M1`, `M2`…) — leadership-facing markers, color-coded with emoji. Numbered in expected completion order based on the current dependency graph. Renumber, split, or merge whenever blockers shift the critical path.

**Sessions** (`SXX`) — scoped work units with explicit bidirectional dependencies:
- `Blocked on:` — what must finish first (omit line entirely if nothing blocks it → ready to pick up)
- `Blocking:` — what it unblocks downstream (omit line if nothing depends on it)

All sessions live under a single `## Sessions` heading — no Available/Blocked split.

## Routing

Two explicit actions: `new` and `update`. The action is **required** whenever a slug is provided — the script errors otherwise. The script echoes `ACTION=` + `MODE=` in its output.

| Invocation                           | Flow |
|--------------------------------------|------|
| `/projects`                          | Dashboard — list all projects from the script output. |
| `/projects <slug> new <description>` | Scaffold a new project. Gather goal/scope from `<description>`, map milestones + sessions + deps, write project.md + initial AUDIT_LOG. |
| `/projects <slug> update <...>`      | Any change or read on an existing project. The skill infers intent from the user's message (view, progress report, completion, restructure, scope change, status). Run the **Drift Check** before writing. |

The skill owns interpretation of the `update` payload. Look at the user's raw message to decide whether they're asking to view state, log progress, complete a session, restructure work, or change scope — then route to the appropriate flow below.

## Rules

- YYYY-MM-DD dates. Update `last_touched` on every doc change.
- **Every change to project.md gets a dated AUDIT_LOG.md entry.** This is the traceability backbone.
- Hyperlink external references: Linear as `[DEF-XXXXX](https://linear.app/...)`, Notion as `[Page name](https://notion.so/...)`, GitHub as `[owner/repo#123](https://github.com/...)`. No bare URLs.
- Preserve the user's language.
- **Goal**: 1–2 sentences, outcome-focused (what's delivered to users/leadership), not implementation.
- **Out of scope**: only list items someone might reasonably assume are included but aren't. Skip the section if nothing fits — never mirror the session list.
- **Never silently rewrite a session to match a completion report.** Run the **Drift Check** first; ask before writing when reported work diverges from scoped intent.
- Be opinionated when the user reports changes — surface consequences (renumbered milestones, newly-ready sessions, broken assumptions), don't just log.

## Graph Maintenance

The graph shows **remaining work only**. Completed sessions live in the `## Completed` table and AUDIT_LOG, never the graph.

Whenever the graph changes (new project, completion, restructure):

- **Remove completed sessions entirely** — node, every edge touching it, and its `style` directive. The graph shrinks as the project progresses.
- **Recalculate batch levels** — sessions whose deps are all done become batch 0.
- **Transitive reduction** — only direct edges. If A → B → C, don't draw A → C.
- **Recompute every remaining session's `Blocking:` line.** A completed session can cascade-unblock work several hops downstream. Stale `Blocking:` lines are the most common drift.
- When a session's last `Blocked on:` dependency clears, delete the line entirely.

## Mermaid Format

`flowchart TB`. Force vertical ordering with invisible subgraphs by batch level:

```
subgraph b0[" "]
    direction LR
    s01([S01 Short name])
    s02([S02 Short name])
end
style b0 fill:none,stroke:none
```

Without subgraphs, Dagre pulls unblocked nodes down next to distant children. Node format: `sXX([SXX Name])` — max 20 chars.

Color-code nodes by milestone using `style` directives, matching the emoji in the milestones table:

| Emoji | Fill | Stroke | Text |
|-------|------|--------|------|
| 🟦 | `#60a5fa` | `#1e40af` | `#1e3a5f` |
| 🟪 | `#c084fc` | `#6b21a8` | `#3b0764` |
| 🟧 | `#fb923c` | `#9a3412` | `#431407` |
| 🟩 | `#4ade80` | `#166534` | `#052e16` |
| 🟥 | `#f87171` | `#991b1b` | `#450a0a` |
| 🟨 | `#facc15` | `#854d0e` | `#422006` |

Reuse colors if more than 6 milestones.

## Scaffolding a new project

The script creates empty files. Use the user's description as intent; ask clarifying questions if needed (goal, scope, constraints). Then:

1. Define milestones as a table — `M#` + emoji + name + status, ordered by expected completion.
2. Break work into sessions with explicit bidirectional deps. Each session names: what it accomplishes, which milestone, what blocks it, what it blocks.
3. Build the dependency graph (see Graph Maintenance + Mermaid Format).
4. Write session entries under one `## Sessions` heading. Format:

   ```
   ### <a id="sXX"></a>SXX — Name

   **Milestone:** 🟧 M3 — Shipped to staging

   Brief description.

   **Blocked on:** [S01](#s01), [S02](#s02)   ← omit if nothing blocks it
   **Blocking:** [S05](#s05), [S09](#s09)     ← omit if nothing depends on it
   ```

   Order roughly by readiness.

5. Empty `## Completed` table: `| Session | Completed | Ref |`
6. Write project.md and the initial AUDIT_LOG entry.

## Drift Check

Runs before any `update` action that touches a session. Compare the user's report to the session's current definition:

1. **Read the session entry** — scope, milestone, blocked/blocking.
2. **Classify** the reported work:
   - **Aligned** — reported outcome matches the session's scoped intent.
   - **Partial** — only part of the scope is done. Ask: close the finished slice as a new session and leave the rest open, or leave the session open and note progress?
   - **Expanded** — scope is done *plus* additional work. Ask: split the extra into a new session, or retroactively widen this session's scope?
   - **Diverged** — the work done is different from what was scoped. Ask: retire this session and create a new one that matches reality, or rewrite the session's scope?
3. **Only proceed** once the user answers any drift questions.

Skip questions only when the classification is clearly **aligned**. When in doubt, ask.

## Completing a session

Trigger: the user reports a session is done ("S04 done, PR #123, ticket DEF-456").

1. Run the **Drift Check**.
2. **Fast path** (aligned): do the mechanical updates without further questions.
   - Delete the session's node, edges, and `style` from the graph. Recalculate batches.
   - Remove the session entry from `## Sessions`.
   - **Refresh every remaining session's dependency lines** — drop the completed session from `Blocked on:`, recompute `Blocking:` (cascades several hops out).
   - Add a row to the Completed table with name, date, PR/ref.
   - Append the full session definition + outcomes + refs to AUDIT_LOG. This is the permanent record.
   - Surface any newly-ready sessions and any milestones now achievable.
3. **Guided path** (partial/expanded/diverged): resolve drift questions first, then run the fast-path steps against the reconciled shape (possibly completing one session and creating/rewriting another in the same turn).

## Reporting progress (mid-session)

Trigger: the user reports work on a session that doesn't close it out.

1. Run the **Drift Check**.
2. If **aligned**, log the progress note to AUDIT_LOG with the session ID and a one-line summary. Update `last_touched`. Do not touch the graph or session entry unless dependencies changed.
3. If **drifted**, resolve questions first. The answer usually lands in one of: update the session's scope, split the session, or restructure.

## Restructuring sessions

When the user reports developments that change scope ("split S04 into two", "S07 needs to wait on a new dep"):

1. Add/remove/rewrite session entries.
2. Update the graph: new nodes, new edges, retire obsolete ones.
3. Recompute `Blocked on:` and `Blocking:` lines on every affected session.
4. Re-evaluate milestone numbering against the new critical path.
5. Log the change and the reasoning to AUDIT_LOG.

## Completing a milestone

Verify all contributing sessions are resolved (done or descoped). Mark complete with a narrative summary. If no milestones remain, ask if the project is `status: complete`.
