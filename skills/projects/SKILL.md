---
name: projects
description: >
  Track multi-milestone projects from planning through completion.
  Use when the user types "/projects" to view the portfolio, create/update a project,
  check status, or hand off a session to /spec-new-feature.
argument-hint: <project-slug> [description]
disable-model-invocation: true
---

# Projects Skill

## Context

!`~/.claude/skills/projects/scripts/projects-setup.sh "$0" "$1"`

Read the project file and AUDIT_LOG at the paths shown above to determine current state.

## What lives where

**project.md** — the active state. What the project is, what needs to happen, and what's done.

- Project goal and scope
- Blockers and constraints
- Milestones (leadership-facing progress markers)
- Sessions (scoped work units with dependencies)
- Mermaid dependency graph flowchart (color-coded by milestone)
- Session definitions with cross-references

**AUDIT_LOG.md** — the historical record. How we got here.

- What changed each session (adds, removes, reorders, scope shifts)
- Decisions made and why
- Update notes from each `/projects <slug>` invocation

This skill tracks _what_, _when_, and _what's blocking_. It does NOT handle technical details — that's `/spec-new-feature`'s job.

## Key Concepts

**Milestones** — Human-leadership-facing progress markers. "We shipped auth." "Beta launched." They prove project progression. Milestones don't dictate execution order.

**Sessions** — Scoped units of work that a human + AI pair tackle together via `/spec-new-feature`. Each session has explicit dependencies on other sessions. A session is either blocked (waiting on prior sessions) or available (all dependencies met, ready to start).

**Parallelization** — Sessions with no mutual dependencies can be worked concurrently. The dependency graph flowchart makes this visible — nodes at the same depth level are batchable. The project maps out the full parallelization potential, but in practice the human picks what makes sense from what's available. After completing sessions, project state updates and new sessions become unblocked.

Sessions contribute to milestones, but the relationship is many-to-many — a session may touch multiple milestones, and a milestone may require sessions at different points in the dependency chain.

## Routing

| MODE        | Action                                                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `dashboard` | Show all projects listed by the script                                                                                                |
| `existing`  | Read project state. Use any additional description from the user to determine intent (status check, update, session completion, etc.) |
| `new`       | Read any description the user provided for intent. Gather goal/scope, map out milestones + sessions + dependencies, write the doc     |

## Rules

- Use YYYY-MM-DD dates. Update `last_touched` on every doc change.
- Don't explore the codebase — that's `/spec-new-feature`'s job.
- No technical details in project.md — focus on what, when, dependencies, and blockers.
- Preserve the user's language.
- Every change to project.md should also get a dated entry in AUDIT_LOG.md explaining what changed and why.

<important if="MODE is new">

The script scaffolded empty project files. Use any description the user included in their `/projects` invocation as intent. Ask clarifying questions if needed (goal, scope, size, constraints). Then:

1. Define milestones as a table — leadership-facing progress markers covering the full arc. Format: `| # | Milestone | Status |` with one row per milestone. Prefix each milestone number with an emoji square color (🟦🟪🟧🟩🟥🟨) — these map directly to the node colors in the dependency graph.
2. Identify blockers and constraints (external dependencies, access needs, unknowns).
3. Break all work into sessions with explicit dependencies. Each session should name: what it accomplishes, which milestone(s) it contributes to, and which other sessions must complete first.
4. Build the **Dependency Graph** flowchart under `### Dependency Graph`. This is the primary visualization — it encodes all three variables: dependencies (arrows), batchable sessions (same level), and milestones (color). Rules:
   - Use `flowchart TB` (top-to-bottom).
   - **Force vertical ordering with invisible subgraphs.** Dagre does NOT respect topological depth — it minimizes edge length, so unblocked nodes get pulled down next to their distant children. The only reliable fix is subgraphs. Group sessions by batch level into subgraphs with `direction LR`, then style them invisible:
     ```
     subgraph b0[" "]
         direction LR
         s01([S01 Upgrade safety])
         s02([S02 1P secrets])
     end
     style b0 fill:none,stroke:none
     ```
     Name subgraphs `b0`, `b1`, `b2`, etc. by batch level. Batch 0 = no dependencies (top row). Batch 1 = depends only on batch-0 nodes. And so on.
   - Node format: `sXX([SXX Short name])` — rounded rectangle, max 20 chars.
   - Draw dependency arrows between nodes: `s02 --> s04`. **Use transitive reduction** — only draw direct edges. If A → B → C, don't draw A → C; the dependency is already implied through B. This keeps the graph clean. (Session definitions still list all dependencies so each session is self-contained for pickup.)
   - Color-code each node by milestone using `style` directives at the bottom. Assign one color per milestone, matching the emoji in the milestones table:
     - 🟦 Blue: `fill:#60a5fa,stroke:#1e40af,color:#1e3a5f`
     - 🟪 Purple: `fill:#c084fc,stroke:#6b21a8,color:#3b0764`
     - 🟧 Orange: `fill:#fb923c,stroke:#9a3412,color:#431407`
     - 🟩 Green: `fill:#4ade80,stroke:#166534,color:#052e16`
     - 🟥 Red: `fill:#f87171,stroke:#991b1b,color:#450a0a`
     - 🟨 Yellow: `fill:#facc15,stroke:#854d0e,color:#422006`
   - If more than 6 milestones, reuse colors for grouped milestones.
   - Completed sessions: restyle to grey `fill:#9ca3af,stroke:#4b5563,color:#1f2937`.
5. Write session **Definitions** below the graph. Each session gets:
   - `#### <a id="sXX"></a>SXX — Name`
   - **Milestone:** which milestone(s) it contributes to — on its own line
   - **Depends on:** `[S01](#s01), [S02](#s02)` (linked) or `—` if none — on its own line, separated from Milestone by a blank line
   - A brief description of the work (no technical detail), also separated by a blank line

   Example format (note the blank lines between each field):

   ```
   #### <a id="s01"></a>S01 — Setup auth

   **Milestone:** M1 — Core infrastructure

   **Depends on:** —

   Stand up authentication service and integrate with the API gateway.
   ```

Iterate with the user, then write both project.md and an initial AUDIT_LOG entry.

</important>

<important if="MODE is existing">

The script returned an existing project. Read project.md and AUDIT_LOG.md, then use any additional description the user provided to determine what they want:

- **No description** → Present project state: milestones progress, available sessions, what's blocked and why. Ask what to do next.
- **Description provided** → Figure out the intent and act accordingly:
  - Add/remove/reorder sessions and milestones as warranted.
  - Update dependencies, mark sessions complete, adjust priorities.
  - Update the dependency graph to reflect changes (new sessions, reordered batches, grey styling for completed nodes).
  - Check if completed sessions cause any milestones to be achieved.
  - Be opinionated about impact — don't just log, surface consequences.
  - Write a dated entry to AUDIT_LOG.md with what changed and why.

</important>

<important if="user wants to complete a session">

Mark the session definition with completion date and any PR references. Update the dependency graph: restyle completed nodes to grey (`fill:#9ca3af,stroke:#4b5563,color:#1f2937`). Then:

- Check if this completion achieves any milestones.
- Show which sessions are now available (their dependencies are all `done`).
- Log to AUDIT_LOG.

</important>

<important if="user wants to complete a milestone">

Verify all contributing sessions are resolved (done or descoped). Mark the milestone complete with a narrative summary. If no milestones remain, ask if the project is complete (`status: complete`). Log to AUDIT_LOG.

</important>

<important if="user wants to pick up a session or hand off to spec-new-feature">

The session must have no unfinished dependencies (all `depends on` sessions are done). Assemble a curated context block with: **Project Goal**, **This Session** (what it accomplishes, which milestone(s) it serves), **What's Already Shipped** (completed sessions, PR numbers + key outcomes), **Blockers & Constraints**, **Relevant Decisions** (from AUDIT_LOG). Curate, don't dump. Frame the work, don't spec it — technical depth is `/spec-new-feature`'s job. Present and ask if ready to invoke `/spec-new-feature`.

</important>
