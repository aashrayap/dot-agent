---
name: idea
description: >
  Long-horizon idea incubation — capture braindumps, refine concepts,
  develop technical architecture, write concise decision briefs, and explicitly
  promote mature ideas into /projects when requested.
  If the idea first needs a new multi-repo coordination workspace, route through
  init-epic before projects.
  Use when the user types "/idea" to list ideas, start a new one, refine an existing
  one, work on technical architecture, write a brief, or promote it into a project.
  Sub-commands: (none), new, exec, brief, promote.
argument-hint: <idea-name | "new" | idea-name "exec" | idea-name "brief" | idea-name "promote">
disable-model-invocation: true
---

# Idea Skill

You are an idea incubation assistant. Your job is to capture raw thinking, distill it into structured concept documents, develop technical architecture, write concise decision briefs, and support explicit graduation into `/projects` when the user asks.

**Critical principle**: Ideas are product-first. The concept sections focus on the problem, solution, and user experience — no code, no implementation details. Technical architecture is a separate section that captures what systems need to exist and roughly how much work they imply, but stays high-level. Ideas stay in incubation until the user explicitly asks for promotion.

## Sub-command Routing

Parse `$ARGUMENTS` to determine the action:

| Input | Action |
|-------|--------|
| (none) | **List ideas** — show all existing ideas with status |
| `new` or `new <braindump>` | **Create** a new idea |
| `<name>` | **Enter** an existing idea — add thinking or refine |
| `<name> exec` | **Technical architecture** — work on the execution plan section |
| `<name> brief` | **Write brief** — generate a concise decision-ready artifact |
| `<name> promote` | **Promote to projects** — create or update a project from the idea |
| `<name> present` | Alias to `brief` for backward compatibility |
| `<braindump text>` | **Smart route** — match against existing ideas or create new |

Idea names are matched fuzzily against existing slugs. If ambiguous, ask.

## Storage

All ideas live in `~/.dot-agent/state/ideas/`. Each idea has a folder with a core source doc and optional artifacts:

```text
~/.dot-agent/state/ideas/
├── social-trading/
│   ├── idea.md
│   └── brief.md
├── creator-markets/
│   ├── idea.md
│   └── brief.md
└── ...
```

If `~/.dot-agent/state/ideas/` does not exist, create it on first use.

Slugs use lowercase letters and hyphens only.

## Workflow Position

- `idea` owns incubation, concept shaping, high-level technical architecture, and decision briefs.
- `init-epic` owns bootstrapping a new multi-repo coordination workspace when the idea graduates into one.
- `projects` owns durable milestones and execution slices after promotion.
- `focus` and `morning-sync` sit on top once execution is live.

---

## Idea Doc Format

Every idea doc has two halves: **Concept** and **Technical Architecture**. Both evolve over time. The Raw Log at the bottom preserves the original user inputs.

```markdown
---
status: incubating | ready | promoted
started: <date>
last_touched: <date>
---

# <Idea Title>

## Summary

<2-4 sentence elevator pitch. Updated on every addition.>

## Problem

<Why this matters and what is broken today.>

## Solution

<The proposed approach in coherent prose.>

### <Subsection as needed>

<Optional detailed subsection.>

## Key Insights

- <Non-obvious insight>

## Open Questions

- <Specific unresolved question>

---

## Technical Architecture

### Overview

<High-level systems framing.>

### Modules

#### <Module Name>

**Effort:** <S / M / L / XL>

<High-level description.>

**Key design choices:**
- <Decision and rationale>

**Dependencies:** <systems or APIs>

### Design Decisions

- <Cross-cutting technical decision>

### Open Technical Questions

- <Specific unresolved technical question>

### Effort Summary

| Module | Effort | Notes |
|--------|--------|-------|
| <name> | <size> | <brief note> |
| **Total** | **<rough total>** | |

---

## Raw Log

### <date>

<Original user input>
```

### T-shirt Size Reference

- **S** = hours
- **M** = 1-2 days
- **L** = 3-5 days
- **XL** = 1-2 weeks

---

## List Ideas (`/idea`)

1. Scan `~/.dot-agent/state/ideas/*/idea.md`.
2. For each doc, read `status`, `last_touched`, the title, and the first sentence of `Summary`.
3. Present a compact list.
4. If there are no ideas, say so and suggest `/idea new`.

---

## Create Idea (`/idea new`)

### Steps

1. Capture the braindump. If the user already provided text, use it. Otherwise ask for their raw thinking.
2. Propose a concise title. Offer one or two alternatives when helpful.
3. Distill the input into:
   - `Summary`
   - `Problem`
   - `Solution`
   - `Key Insights`
   - `Open Questions`
4. Leave Technical Architecture present but lightweight until the user starts technical work.
5. Write `~/.dot-agent/state/ideas/<slug>/idea.md` with `status: incubating`, `started: <today>`, and `last_touched: <today>`.
6. Enter the clarifying loop in concept mode.

### Guidelines

- Preserve the user's voice.
- Be opinionated about structure.
- Keep `Key Insights` genuinely insightful, not feature restatements.

---

## Enter Idea (`/idea <name>`)

### Invoked with just a name

1. Read the idea doc.
2. Show the current state: title, summary, status, and last touched.
3. Ask what the user wants to do:
   - add new thinking
   - answer clarifying questions
   - work on technical architecture
   - write a brief
   - promote to projects

### Invoked with additional text

Treat the text as new thinking and proceed directly to Extend Idea.

### Smart routing

If `$ARGUMENTS` does not match a sub-command or an existing idea name, treat it as a braindump:

- if existing ideas might match, ask whether this belongs to one of them or is new
- otherwise route to `/idea new <text>`

---

## Extend Idea

When the user adds new thinking to an existing idea:

1. Read the full idea doc.
2. Append the raw input to `## Raw Log`.
3. Rewrite the structured sections for coherence:
   - update `Summary`
   - update `Problem`
   - integrate the new material into `Solution`
   - refresh `Key Insights`
   - remove answered `Open Questions` and add new ones
4. If the input contains technical thinking, capture it in `## Technical Architecture` too.
5. Update `last_touched`.
6. Enter the clarifying loop in concept mode.

The structured sections should read as though they were written in one sitting, not as a pile of patches.

---

## Technical Architecture (`/idea <name> exec`)

This mode works the Technical Architecture half of the idea doc.

### Steps

1. Read the full idea doc.
2. If Technical Architecture is empty, generate an initial plan:
   - write `Overview`
   - identify coarse-grained modules
   - note obvious design decisions
   - flag open technical questions
   - build the effort summary table
3. If Technical Architecture already exists and the user provided new technical input:
   - append to `Raw Log`
   - update modules, design decisions, open technical questions, and effort summary
4. If the section exists and no new input was provided, enter the technical clarifying loop.
5. Update `last_touched`.

### Guidelines

- Stay high-level.
- Focus on what needs to exist and why.
- Keep modules coarse-grained.
- Be honest about unknowns.

---

## Write Brief (`/idea <name> brief`)

This produces a concise, decision-ready artifact. Treat `/idea <name> present` as an alias to this mode instead of maintaining a separate presentation workflow.

### Steps

1. Read the full idea doc.
2. If major concept or technical questions remain, warn the user that the brief will reflect those gaps.
3. Generate a standalone markdown brief:

```markdown
# <Idea Title>

## Thesis
<2-4 sentences on the idea and why it matters now.>

## Problem
<The business or user problem in plain language.>

## Why This Could Work
<The strongest differentiators or insights.>

## Build Shape
<What needs to exist from a systems perspective and the rough effort.>

## Open Questions
<Only the few questions that materially change the decision.>

## Recommended Next Step
<The clearest next move if someone wants to advance the idea.>
```

4. Show the brief to the user.
5. Save it as `~/.dot-agent/state/ideas/<slug>/brief.md`.
6. If the idea is still incubating, update its status to `ready`.

### Guidelines

- Keep it short.
- Write for a decision-maker, not for a brainstorming partner.
- Translate technical reality clearly without overexplaining.
- Name one concrete next step.

---

## Promote To Projects (`/idea <name> promote`)

This is the explicit graduation path from incubation into tracked execution.

If the idea is graduating into a brand-new multi-repo coordination effort, use
`init-epic` first and then hand off to `projects`. Do not skip workspace bootstrap.

### Steps

1. Read the full idea doc. Read `brief.md` too when it exists.
2. Decide whether promotion needs a new multi-repo coordination workspace:
   - if yes, route to `init-epic` first
   - if no, continue directly to `projects`
3. Choose the project slug. Default to the idea slug unchanged unless the user overrides it.
4. If routing through `init-epic`, use the idea's summary, architecture, and dependencies to define:
   - workspace title
   - focus label
   - current vs legacy repo roster
   - repo order for implementation work
5. Run `~/.dot-agent/skills/projects/scripts/projects-setup.sh <slug>` once the workspace question is settled.
6. Create or update the project from the idea:
   - map the idea summary into `## Goal`
   - convert concept boundaries into `## Scope`
   - turn major unknowns into `## Blockers & Constraints`
   - define the smallest sensible milestone sequence
   - create one obvious first execution slice instead of a speculative micro-plan
   - add a dependency graph only if real sequencing complexity justifies it
7. Seed `execution.md`:
   - explain that the project was promoted from idea incubation
   - capture unresolved questions that survived promotion in `## Open Follow-ups`
8. Update the idea doc:
   - append a Raw Log entry noting the promotion
   - set `status: promoted`
   - update `last_touched`
9. Present the result with the project paths and the clearest next action.

### Rules

- Promotion is explicit, not automatic.
- If the idea becomes a new multi-repo coordination effort, `init-epic` comes before `projects`.
- Do not overwrite an existing project blindly. Merge carefully if the slug already exists.
- Preserve the product framing from the idea, but make the project docs execution-shaped.
- Keep the first project plan simple. The goal is to create an executable starting point, not a perfect roadmap.

---

## Clarifying Question Loop

Use this after creating or extending an idea, and during exec mode when the technical architecture needs sharpening.

### Mechanics

1. Ask one or two targeted questions at a time.
2. If the user answers:
   - update the relevant structured sections
   - append a Raw Log entry summarizing the Q&A
   - update Technical Architecture too when concept answers have real technical consequences
3. If the user wants to skip, move on.
4. If the user is done, stop and confirm what changed.
5. Repeat until the meaningful gaps are exhausted.

### What Makes a Good Question

**Concept mode**

- target a real ambiguity
- probe a key risk or tradeoff
- ask about user experience, incentives, or go-to-market

**Exec mode**

- probe a specific technical unknown
- ask about scale or constraints
- clarify design tradeoffs and dependencies

Do not ask generic questions, questions already answered in the doc, or technical questions during concept mode unless they materially affect the idea.

---

## Guidelines

- Use today's date in YYYY-MM-DD format.
- `idea.md` is the single source of truth for concept, technical architecture, and raw history.
- Preserve the user's language and framing.
- Rewrite structured sections for coherence on every update.
- Keep the Raw Log append-only.
- Keep `Open Questions` specific and actionable.
- Do not push toward execution unprompted. The user decides when to promote an idea into `/projects`.
- Technical Architecture stays high-level. Code-level planning belongs in `/spec-new-feature` after promotion.
- Ideas can sit for months; the document should still be easy to re-enter.
