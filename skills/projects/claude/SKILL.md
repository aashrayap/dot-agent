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

!`~/.claude/skills/projects/scripts/projects-setup.sh "$1"`

Read the project file and AUDIT_LOG at the paths shown above to determine current state.

## Structure

**project.md** — active state: goal, scope, blockers, milestones, dependency graph, available/blocked sessions, and completed table. The scaffolded template shows the expected structure and formats.

**AUDIT_LOG.md** — historical record: what changed each session, decisions made, and why.

Projects live under `~/.dot-agent/state/projects/` so both Claude and Codex on the same machine share the same project state.

This skill tracks _what_, _when_, and _what's blocking_. Technical details and codebase exploration are `/spec-new-feature`'s job.

## Key Concepts

**Milestones** — Leadership-facing progress markers ("We shipped auth"). They prove progression but don't dictate execution order.

**Sessions** — Scoped work units tackled via `/spec-new-feature`. Each has explicit dependencies. Sessions with no mutual dependencies can be worked concurrently — the dependency graph makes parallelization visible.

## Routing

| MODE        | Action                                                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `dashboard` | Show all projects listed by the script                                                                                                |
| `existing`  | Read project state. Use any additional description from the user to determine intent (status check, update, session completion, etc.) |
| `new`       | Read any description the user provided for intent. Gather goal/scope, map out milestones + sessions + dependencies, write the doc     |

## Rules

- Use YYYY-MM-DD dates. Update `last_touched` on every doc change.
- Every change to project.md gets a dated AUDIT_LOG.md entry explaining what changed and why.
- Hyperlink all external references: Linear as `[DEF-XXXXX](https://linear.app/...)`, Notion as `[Page name](https://notion.so/...)`, etc. No bare URLs.
- Preserve the user's language.

### Graph Maintenance

These rules apply whenever the dependency graph changes (new project, session completion, restructuring):

- **Remove completed sessions entirely** — delete node, edges, and style directive.
- **Recalculate batch levels** — sessions whose dependencies are all completed become batch 0 (top row). Renumber subgraphs accordingly.
- **Transitive reduction** — only draw direct edges. If A → B → C, don't draw A → C.
- Move newly unblocked sessions from `## Blocked Sessions` to `## Available Sessions`.

### Mermaid Format

Use `flowchart TB`. Force vertical ordering with invisible subgraphs by batch level:

```
subgraph b0[" "]
    direction LR
    s01([S01 Short name])
    s02([S02 Short name])
end
style b0 fill:none,stroke:none
```

Without subgraphs, Dagre pulls unblocked nodes down next to distant children. Node format: `sXX([SXX Name])` — max 20 chars.

Color-code nodes by milestone using `style` directives. One color per milestone, matching the emoji in the milestones table:

| Emoji | Fill | Stroke | Text |
|-------|------|--------|------|
| 🟦 | `#60a5fa` | `#1e40af` | `#1e3a5f` |
| 🟪 | `#c084fc` | `#6b21a8` | `#3b0764` |
| 🟧 | `#fb923c` | `#9a3412` | `#431407` |
| 🟩 | `#4ade80` | `#166534` | `#052e16` |
| 🟥 | `#f87171` | `#991b1b` | `#450a0a` |
| 🟨 | `#facc15` | `#854d0e` | `#422006` |

If more than 6 milestones, reuse colors.

<important if="MODE is new">

The script scaffolded empty project files. Use any description from the user's invocation as intent. Ask clarifying questions if needed (goal, scope, constraints). Then:

1. Define milestones as a table — prefix each with an emoji color (🟦🟪🟧🟩🟥🟨) mapping to the graph node colors.
2. Identify blockers and constraints.
3. Break all work into sessions with explicit dependencies. Each session names: what it accomplishes, which milestone(s), and which sessions must complete first.
4. Build the dependency graph (see Mermaid Format and Graph Maintenance above).
5. Write session details under `## Available Sessions` and `## Blocked Sessions`. Format:

   ```
   #### <a id="sXX"></a>SXX — Name

   **Milestone:** 🟦 M1 — Name

   Brief description (no technical detail).

   **Blocked on:** [S01](#s01), [S02](#s02)   ← only for blocked sessions
   ```

6. Write the `## Completed` table (empty initially): `| Session | Completed | Ref |`

Iterate with the user, then write both project.md and an initial AUDIT_LOG entry.

</important>

<important if="MODE is existing">

Read project.md and AUDIT_LOG.md, then determine intent from any description the user provided:

- **No description** → Present project state: milestones progress, available sessions, what's blocked and why. Ask what to do next.
- **Description provided** → Act accordingly: add/remove/reorder sessions and milestones, update dependencies, mark sessions complete, adjust priorities. Be opinionated about impact — surface consequences, don't just log.

</important>

<important if="user wants to complete a session">

1. Apply Graph Maintenance rules (remove node, recalculate batches, move unblocked sessions to Available).
2. Remove the session definition from Available/Blocked.
3. Add a row to the Completed table with session name, date, and PR/ref.
4. Log to AUDIT_LOG — include the full session definition (name, milestone, description), completion date, PR refs, and outcomes. This is the permanent historical record.
5. Check if this achieves any milestones. Show which sessions are now available.

</important>

<important if="user wants to complete a milestone">

Verify all contributing sessions are resolved (done or descoped). Mark the milestone complete with a narrative summary. If no milestones remain, ask if the project is complete (`status: complete`).

</important>

<important if="user wants to pick up a session or hand off to spec-new-feature">

The session must have no unfinished dependencies. Assemble a curated context block with: **Project Goal**, **This Session** (what it accomplishes, which milestone(s)), **What's Already Shipped** (completed sessions, PR numbers + key outcomes), **Blockers & Constraints**, **Relevant Decisions** (from AUDIT_LOG). Curate, don't dump. Present the context block and ask whether to invoke `/spec-new-feature <session-slug>`.

</important>
