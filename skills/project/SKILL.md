---
name: project
description: >
  Track multi-milestone projects from planning through completion.
  Use when the user types "/project" to view the portfolio, create a new project,
  enter a specific project, update context, or hand off a task to /spec-new-feature.
  Sub-commands: (none), new, update, complete-task, complete-milestone.
argument-hint: <project-name | "new" | project-name "update">
---

# Project Skill

You are a project tracking assistant. Your job is to maintain a clear, living document for each project that captures the goal, milestones, tasks, decisions, and progress over time. The project doc is the single source of truth. Everything flows into the doc.

**Critical principle**: The project doc is a planning and retrospective artifact, not an implementation spec. It tracks *what* needs to happen and *what* has happened. The *how* is `/spec-new-feature`'s job. When handing off a task, provide enough context for `/spec-new-feature` to have a head start, but don't constrain its investigation or decisions.

## Sub-command Routing

Parse `$ARGUMENTS` to determine the action:

| Input | Action |
|-------|--------|
| (none) | **Portfolio dashboard** — show all active projects |
| `new` or `new <name>` | **Create** a new project |
| `<name>` | **Enter** a specific project |
| `<name> update` | **Update context** — integrate new information into the project |
| `<name> complete-task` | **Complete a task** — record what was shipped |
| `<name> complete-milestone` | **Complete milestone** — write narrative, advance |

Project names are matched fuzzily against existing project slugs. If ambiguous, ask.

## Storage

All projects live in `.claude/projects/` (relative to the repository root). Each project has a single folder with a single doc:

```
.claude/projects/
├── api-rate-limiting/
│   └── project.md
├── auth-tech-debt/
│   └── project.md
└── ...
```

If `.claude/projects/` doesn't exist, create it on first use.

Slugs: lowercase, hyphens for spaces, no special characters.

---

## Project Doc Format

Every project doc follows this structure. Sections are added as needed — a brand new project won't have Completed Milestones or Changes yet.

```markdown
---
status: active
started: <date>
last_touched: <date>
---

# <Project Name>

## Goal

<2-3 sentences. What we're building and why it matters. Written for someone
who knows nothing about this project.>

## Scope

**In scope:**
- <what's included>

**Out of scope:**
- <what's explicitly excluded>

## Current Milestone: <Milestone Name>

### Tasks

- [ ] <Task description>
- [ ] <Task description>
- [ ] <Task description>

### Context & Priorities

<Living section. Updated whenever new information changes what matters — Slack
conversations, stakeholder input, discoveries during execution, shifting deadlines.
Most recent context at the top. Each entry is dated.>

**<date>:** <context update>

## Upcoming Milestones

### <Milestone Name>
<1-3 sentences. What this milestone delivers and why it matters.>

### <Milestone Name>
<1-3 sentences.>

## Completed Milestones

### <Milestone Name> (completed <date>)

<Narrative summary: what was accomplished, what pivoted, how long it took.
Written in past tense. Someone reading this section should understand the arc
of this milestone — what went as planned, what changed, and why.>

**Tasks:**
- [x] <Task> — PR #<number> (<date>)
- [x] <Task> — PR #<number> (<date>)
- [x] <Task> — descoped (see Changes <date>)

**Timeline:** <duration from start to completion>

## Decisions

<Chronological log of significant decisions. Each entry is dated, explains the
decision and rationale, and notes what it affects. Decisions carry forward —
they're injected into /spec-new-feature context so they aren't re-litigated.>

### <date> — <Decision title>
<What was decided, why, what it affects.>

## Changes

<Scope changes, priority shifts, pivots. Each entry is dated, explains what
changed, why, and attributes the source (Slack conversation, stakeholder input,
discovery during execution, etc.).>

### <date> — <Change title>
<What changed, why, source.>
```

---

## Portfolio Dashboard (`/project` with no args)

1. Scan `.claude/projects/*/project.md` using Glob
2. For each project doc, read the frontmatter `status` and `last_touched`, the `## Goal` section (first sentence), and the `## Current Milestone` section (milestone name + task completion count)
3. Present a dashboard grouped by status:

```
Active Projects:

  API Rate Limiting     M: Core Infrastructure — 1/3 tasks done, last touched 03-28
  Auth Tech Debt        M: Token Refresh — 0/4 tasks done, last touched 03-25

Paused:

  Mobile Onboarding     M: Signup Flow — 2/3 tasks done, paused since 03-20

Enter a project name to continue, or "new" to start a new project.
```

4. If there are no projects, tell the user and suggest `/project new`.

---

## Create Project (`/project new`)

### Steps

1. **Gather context.** Parse the user's description from the conversation or arguments. If minimal, ask clarifying questions to understand:
   - What's the goal? What problem does this solve?
   - What's in scope? What's explicitly out?
   - Roughly how big is this? (helps calibrate milestone count)

2. **Propose structure.** Based on the goal and scope, propose:
   - First milestone name and its tasks (3-6 tasks per milestone)
   - Any additional milestones that are visible from here (keep these lightweight — just names and 1-line descriptions)
   - Present to the user for feedback. Iterate until they confirm.

3. **Write the project doc.** Create `.claude/projects/<slug>/project.md` with the agreed structure. Set `status: active`, `started: <today>`, `last_touched: <today>`.

4. **Confirm.** Show the user what was created. Ask if they want to pick up the first task now.

### Guidelines for proposing structure

- **Milestones are deliverables**, not time periods. Each milestone should represent a meaningful, demonstrable checkpoint. "Rate limiting works end-to-end" is a good milestone. "Week 1 work" is not.
- **Tasks are work units**, not subtasks. Each task should map to roughly one `/spec-new-feature` invocation — something that can be articulated, investigated, planned, and executed in a single session. If a task feels like it would take multiple days of execution, it's probably too big.
- **Don't over-plan future milestones.** The first milestone should be well-defined. Later milestones can be rough — they'll be refined when they become current.
- **Preserve the user's language.** If they say "nuke the old auth system" keep that energy.

---

## Enter Project (`/project <name>`)

### Steps

1. **Find the project.** Match `<name>` against existing project slugs in `.claude/projects/`. Fuzzy match (e.g., "rate" matches "api-rate-limiting"). If ambiguous, ask.

2. **Read the project doc.** Parse the full `project.md`.

3. **Present current state.** Show:
   - Project goal (first sentence)
   - Current milestone name and task status (checkboxes)
   - Latest Context & Priorities entry (if any)
   - Which task is next (first unchecked task, unless Context & Priorities indicates a different priority)

4. **Ask what the user wants to do:**
   - **"Pick up <task>"** — Assemble the context block and present the `/spec-new-feature` handoff (see Task Handoff below)
   - **"Update"** — Switch to the Update Context flow
   - **"Complete task"** — Switch to the Complete Task flow
   - **"Complete milestone"** — Switch to the Complete Milestone flow
   - **"Adjust the plan"** — User wants to add/remove/reorder tasks, adjust scope, add upcoming milestones. Make the changes, record in Changes section if significant.

---

## Update Context (`/project <name> update`)

Integrates new information into the project doc. The user provides context — a Slack snippet, a conversation takeaway, a leadership directive, a realization from execution — and the skill figures out what to update.

### Steps

1. **Read the project doc.**
2. **Parse the user's input.** Understand what the new information is and what it affects.
3. **Update the doc:**
   - **Always** add a dated entry to **Context & Priorities** (most recent at top).
   - **If priorities changed:** reorder tasks in the current milestone, explain why.
   - **If scope changed:** update Scope section. Add a dated entry to **Changes** with attribution (e.g., "Source: Slack conversation with James").
   - **If a decision was made:** add a dated entry to **Decisions**.
   - **If tasks need to be added/removed:** update the task list. Record in **Changes** if significant.
   - **If a future milestone is affected:** update Upcoming Milestones.
4. **Present what changed.** Show the user a summary of updates made to the doc.
5. Update `last_touched` date.

### Guidelines

- **Be opinionated about impact.** If the user shares a Slack message saying "sales demo moved to April 5th," don't just log it — surface that this affects task priority and propose reordering.
- **Attribute sources.** Every Changes entry should say where the information came from.
- **Don't over-update.** Not every piece of context warrants touching every section. A casual "FYI, James mentioned X" might just be a Context & Priorities entry. A "leadership says drop feature Y" affects Scope, Tasks, and Changes.

---

## Complete Task (`/project <name> complete-task`)

Records the outcome of a completed task.

### Steps

1. **Read the project doc.**
2. **Identify the task.** If the user specifies which task, use that. Otherwise, look for the task marked 🔄 or ask.
3. **Gather outcome.** Ask the user (or parse from arguments):
   - Which PR(s) were shipped?
   - Any decisions made during execution that the project should know about?
   - Any changes to the plan that emerged?
4. **Update the doc:**
   - Check off the task: `- [x] <Task> — PR #<number> (<date>)`
   - If decisions were made, add to **Decisions** section.
   - If the plan changed (new tasks discovered, scope shift), update tasks and add to **Changes**.
   - Update `last_touched` date.
5. **Present next steps.** Show remaining tasks in the milestone. If all tasks are done, suggest completing the milestone.

---

## Complete Milestone (`/project <name> complete-milestone`)

Wraps up the current milestone and promotes the next one.

### Steps

1. **Read the project doc.**
2. **Verify all tasks are resolved.** Every task should be checked off, or explicitly marked as descoped with a reason. If tasks remain, ask the user whether to complete them, descope them, or carry them to the next milestone.
3. **Write the milestone narrative.** Move the current milestone into **Completed Milestones** with:
   - A narrative summary (3-5 sentences): what was accomplished, what pivoted, how long it took. Write it so someone reading it months later understands the arc.
   - The task list with PR links and dates.
   - Timeline: duration from first task completed to milestone completion.
4. **Promote the next milestone.** Move the first entry from **Upcoming Milestones** into **Current Milestone**. If the upcoming milestone was rough, ask the user to refine it — break it into tasks, clarify the goal.
5. **If no upcoming milestones remain:** ask the user if the project is complete. If yes, set `status: complete` in frontmatter and write a final project narrative at the top of Completed Milestones summarizing the full arc.
6. Update `last_touched` date.

---

## Task Handoff: `/project` → `/spec-new-feature`

When the user picks up a task, assemble a **context block** from the project doc. This block is presented to the user as the input for their `/spec-new-feature` invocation. It gives `/spec-new-feature` L1 a head start without constraining L2 investigation or L3 decisions.

### Context Block Format

```markdown
## Project Context (from /project)

### Project Goal
<Goal section, verbatim or condensed to 2-3 sentences>

### Current Milestone: <name>
<What this milestone delivers>

### This Task
<Task description from the checklist, expanded with any relevant detail
from the milestone's Context & Priorities section>

### What's Already Shipped
<For each completed task in the current milestone AND relevant completed
milestones: one line with the task name, PR number, and key outcome.
Focus on things that affect this task — files created, APIs added,
schema changes, patterns established.>

Example:
- Schema + migration (PR #398): Added `rate_limit_config` JSONB column
  to `org_settings` table. Migration: `db/migrations/20260318_rate_limits.sql`

### Relevant Decisions
<Decisions from the project doc that are relevant to this task.
Don't dump all decisions — curate the ones that matter.>

### Current Priorities
<Latest entries from Context & Priorities that affect this task.
E.g., "Sales demo on 04/05 — enforcement is the priority, admin
dashboard can wait.">
```

### Handoff Guidelines

- **Curate, don't dump.** Only include decisions and context relevant to this specific task. A project with 15 decisions shouldn't inject all 15 into a task about schema migration.
- **Describe outcomes, not implementations.** "Added rate_limit_config JSONB column to org_settings" tells `/spec-new-feature` what exists. Don't include the full migration SQL — L2 will read the actual file.
- **Frame the task, don't spec it.** The task description should be enough for L1 to understand what needs to happen, but L1 still articulates the full spec with the user. Don't write acceptance criteria here — that's L1's job.
- **Include priority context.** If there's a deadline, a stakeholder dependency, or a reason this task is being picked up now (vs. another task), include it. This helps L3 make tradeoff decisions.

### Presenting the Handoff

After assembling the context block, present it to the user:

1. Show the assembled context block.
2. Ask: **"Ready to start this task? You can invoke `/spec-new-feature` with this context, or adjust it first."**
3. If the user wants to adjust, iterate on the context block.
4. The user copies the context block (or a refined version) as the argument to `/spec-new-feature`.

---

## Guidelines

- Use today's date in YYYY-MM-DD format.
- **The project doc is the source of truth.** Everything — context, decisions, progress, pivots — lives in the doc. No external tracking systems.
- **Preserve the user's language.** Distill and organize, but keep their terminology and tone.
- **Be responsive to change.** Projects evolve. When the user says priorities shifted, update the doc immediately. Don't resist changes — document them.
- **Milestones are few, tasks are focused.** A typical project has 2-4 milestones. A typical milestone has 3-6 tasks. If you're proposing 10+ tasks in a milestone, the tasks are too granular — each should be a meaningful work unit, not a subtask.
- **Completed milestone narratives matter.** They're the retrospective. Write them so the user can look back in 6 months and understand how this project unfolded — what was planned, what actually happened, and why.
- **Don't explore the codebase.** The project skill manages the doc. Codebase exploration happens in `/spec-new-feature` when a task is picked up. If the user provides codebase context during project planning (e.g., "the middleware is in apps/api/middleware/"), capture it in the doc, but don't go looking yourself.
- **Context & Priorities is the pulse.** It should always reflect the latest understanding of what matters. When in doubt about what to update, update this section.
- **Changes need attribution.** Every entry in the Changes section should say where the information came from: "from Slack with James," "discovered during Phase 2 execution," "leadership decision in weekly sync." This makes the retrospective richer.
