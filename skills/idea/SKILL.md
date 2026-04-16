---
name: idea
description: >
  Long-horizon idea incubation — capture braindumps, refine concepts,
  develop technical architecture, write leadership-ready decision briefs,
  bridge mature ideas into /spec-new-feature, and explicitly promote mature
  ideas into /projects when requested.
  If the idea first needs a new multi-repo coordination workspace, route through
  init-epic before projects. When an idea appears ready for execution, remind
  the user that promotion is available so they do not have to remember the
  command themselves.
  Use when the user types "/idea" to list ideas, start a new one, refine an existing
  one, work on technical architecture, write a brief, write a high-level spec,
  create an optional plan, or promote it into roadmap/projects. Sub-commands: (none), new, exec, brief, spec,
  plan, promote.
argument-hint: <idea-name | "new" | idea-name "exec" | idea-name "brief" | idea-name "spec" | idea-name "plan" | idea-name "promote">
disable-model-invocation: true
---

# Idea Skill

## Composes With

- Parent: user braindumps, roadmap rows, and morning-sync discoveries.
- Children: `roadmap.md`, `projects`, and `spec-new-feature`.
- Uses format from: none.
- Reads state from: `~/.dot-agent/state/ideas/<slug>/`.
- Writes through: idea artifact files only: `idea.md`, `brief.md`, `spec.md`, optional `plan.md`.
- Hands off to: `roadmap.md` for daily work, `projects` for durable work, and `spec-new-feature` when codebase grounding is required.
- Receives back from: `projects` and `execution-review` as delivery context; concept/spec changes still require user approval.

You are an idea incubation assistant. Your job is to capture raw thinking, distill it into structured concept documents, develop technical architecture, write leadership-ready decision briefs, prepare clean handoffs into `/spec-new-feature`, and support explicit graduation into `/projects` when the user asks.

**Critical principle**: Ideas are product-first. The concept sections focus on the problem, solution, user experience, personas, and strategic thesis — no code, no implementation details. Technical architecture is a separate section that captures what systems need to exist and roughly how much work they imply, but stays high-level. Code-grounded planning belongs in `/spec-new-feature`, not in the idea doc. Ideas stay in incubation until the user explicitly asks for promotion.

## Sub-command Routing

Parse `$ARGUMENTS` to determine the action:

| Input | Action |
|-------|--------|
| (none) | **List ideas** — show all existing ideas with status |
| `new` or `new <braindump>` | **Create** a new idea |
| `<name>` | **Enter** an existing idea — add thinking or refine |
| `<name> exec` | Compatibility alias to `spec` |
| `<name> brief` | **Write brief** — generate a concise decision-ready artifact |
| `<name> spec` | **Write spec** — create or refine high-level technical `spec.md` |
| `<name> plan` | **Plan** — create optional `plan.md` or route to `/spec-new-feature` |
| `<name> promote` | **Promote** — add roadmap row first; create project only when durable |
| `<name> present` | Alias to `brief` for backward compatibility |
| `<braindump text>` | **Smart route** — match against existing ideas or create new |

Idea names are matched fuzzily against existing slugs. If ambiguous, ask.

## Storage

All ideas live in `~/.dot-agent/state/ideas/`. Each idea has a folder with a core source doc and optional artifacts:

```text
~/.dot-agent/state/ideas/
├── social-trading/
│   ├── idea.md
│   ├── brief.md
│   ├── spec.md
│   └── plan.md
├── creator-markets/
│   ├── idea.md
│   └── brief.md
└── ...
```

If `~/.dot-agent/state/ideas/` does not exist, create it on first use.

Slugs use lowercase letters and hyphens only.

## Workflow Position

- `idea` owns incubation, concept shaping, high-level technical specs, decision briefs, and optional pre-promotion plans.
- `spec-new-feature` owns approved spec, decontaminated research, design, code-grounded tasks, and optional execution.
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
4. If the idea is already `ready`, or if the doc already has a clear brief and execution-shaped architecture, explicitly ask whether they want to promote it now.

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
7. If the updated idea now looks execution-ready, explicitly remind the user that promotion is available.

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
6. If the architecture now points toward real execution work, ask whether they want to promote the idea now.

### Guidelines

- Stay high-level.
- Focus on what needs to exist and why.
- Keep modules coarse-grained.
- Be honest about unknowns.

---

## Write Brief (`/idea <name> brief`)

This produces a leadership-ready artifact. Treat `/idea <name> present` as an alias to this mode instead of maintaining a separate presentation workflow.

The brief is product-facing. It should stand on its own as the pitch for why the idea matters, who it unlocks, how the rollout can be staged, and what decision should happen next. Do not let it become an engineering spec.

### Steps

1. Read the full idea doc.
2. If major concept or technical questions remain, warn the user that the brief will reflect those gaps.
3. Generate a standalone markdown brief. Default to the concise structure below unless the user explicitly asks for a smaller memo:

```markdown
# <Idea Title>

## Tagline
> <one sentence capturing the endgame product>

## Thesis
<2-4 sentences on the opportunity, why now, and why this shape.>

## The Pitch
- <market/user/problem framing with concrete numbers when available>
- <what was blocked before>
- <what this unlocks now>
- <how it ladders into the broader strategy>

## Personas
| Persona | What they get |
|---------|---------------|

## Why Current Options Do Not Work
| Problem | Consequence |
|---------|-------------|

## Staged Rollout
| Label | Milestone | Delivers | Why it matters | Personas unlocked | Timeline |
|-------|-----------|----------|----------------|-------------------|----------|

## Blockers
| Milestone | Blocker | Why it matters |
|-----------|---------|----------------|

## Open Questions
| Question | Impact | Resolution path |
|----------|--------|-----------------|

## Success Metric
**<one concrete target>**

## Revenue / Strategic Value
<How value is captured, or why this compounds even without direct revenue.>

## Recommended Next Step
<The clearest next move if someone wants to advance the idea.>
```

4. Show the brief to the user.
5. Save it as `~/.dot-agent/state/ideas/<slug>/brief.md`.
6. If the idea is still incubating, update its status to `ready`.
7. Explicitly ask whether they want to promote the idea now. Mention that promotion may route through `init-epic` first for a new multi-repo coordination effort.

### Guidelines

- Keep it concise, but complete enough for a decision-maker to judge.
- Write for a decision-maker, not for a brainstorming partner.
- Translate technical reality clearly without overexplaining.
- Tie every major feature or milestone back to a persona or strategic value.
- Milestones should be independently marketable when possible, not just internal engineering phases.
- Be honest about unknowns. Product-level unknowns stay in the brief; technical unknowns should point back to Technical Architecture or `/spec-new-feature`.
- Name one concrete next step.

---

## Write Spec (`/idea <name> spec`)

This mode creates or refines `~/.dot-agent/state/ideas/<slug>/spec.md`.

`spec.md` is a Sushant-style high-level technical spec. It is not
`spec-new-feature/01_spec.md` and it is not a code task plan.

### Steps

1. Read the full idea doc and `brief.md` when present.
2. Treat `/idea <name> exec` as a compatibility alias to this mode.
3. Check whether the concept is ready enough for technical specification:
   - problem, user, and acceptance shape are clear
   - major product unknowns are either answered or explicitly listed
   - implementation unknowns are separable from product unknowns
4. Write or refresh `~/.dot-agent/state/ideas/<slug>/spec.md`:

```markdown
# <Idea Title> — Spec

## Overview
<technical framing in 1-2 paragraphs>

## Modules

### <Module>

**Effort:** S / M / L / XL

<responsibility, boundary, and why it exists>

**Key design choices:**
- <decision and rationale>

**Dependencies:** <systems/APIs/repos>

## Design Decisions

- <cross-cutting decision>

## Open Technical Questions

- <question that could change the build>

## Effort Summary

| Module | Effort | Notes |
|--------|--------|-------|
```

5. Tell the user whether the next move is:
   - answer concept questions in `/idea`
   - deepen the spec with `/idea <name> spec`
   - create a pre-promotion plan with `/idea <name> plan`
   - start `/spec-new-feature <slug>` when repo/code grounding is needed

### Rules

- Do not write code-level tasks here.
- Do not duplicate `/spec-new-feature` artifact names inside the idea directory.
- Preserve product language from the idea; make uncertainties explicit instead of smoothing them over.

---

## Planning Bridge (`/idea <name> plan`)

Use this when the user asks for implementation order, repo structure, task breakdown, or what to build first.

1. Read the idea doc, `brief.md`, and `spec.md` if present.
2. If the user is still shaping the product, route back to `/idea <name>` or `/idea <name> brief`.
3. If there is no repo yet or the user only needs pre-promotion execution shape, write `~/.dot-agent/state/ideas/<slug>/plan.md`:

```markdown
# <Idea Title> — Plan

## Build Shape
<what must exist, without codebase-specific tasking>

## Execution Order
| Step | Outcome | Depends On | Notes |
|------|---------|------------|-------|

## Promotion Target
Roadmap row first; project only if durable execution memory is needed.
```

4. If the user needs code-grounded tasks, route to `/spec-new-feature`; that workflow owns codebase research, design, and task breakdown.
5. If the idea has already become durable execution work, offer `/idea <name> promote` so roadmap/projects can own live state.

This bridge exists to prevent a third planning surface from growing inside `idea`.

---

## Promote To Projects (`/idea <name> promote`)

This is the explicit graduation path from incubation into tracked execution.

If the idea is graduating into a brand-new multi-repo coordination effort, use
`init-epic` first and then hand off to `projects`. Do not skip workspace bootstrap.

### Steps

1. Read the full idea doc. Read `brief.md`, `spec.md`, and `plan.md` too when they exist.
2. Add or propose a row in `~/.dot-agent/state/collab/roadmap.md` first.
3. Decide whether promotion also needs a project:
   - spans multiple days
   - needs PR/pivot/follow-up memory
   - needs `/spec-new-feature`
   - crosses repositories
   - has durable decisions worth preserving
4. Decide whether promotion needs a new multi-repo coordination workspace:
   - if yes, route to `init-epic` first
   - if no project is needed, stop after the roadmap row
   - if a project is needed, continue to `projects`
5. Choose the project slug. Default to the idea slug unchanged unless the user overrides it.
6. If routing through `init-epic`, use the idea's summary, architecture, and dependencies to define:
   - workspace title
   - focus label
   - current vs legacy repo roster
   - repo order for implementation work
7. Run `~/.dot-agent/skills/projects/scripts/projects-setup.sh <slug>` once the workspace question is settled.
8. Create or update the thin project from the idea:
   - map the idea summary into `## Why`
   - map `plan.md` or `spec.md` into `## Current Slice`
   - fill idea/spec/repo links
   - capture unresolved questions in `## Open Follow-ups`
9. Update the idea doc:
   - append a Raw Log entry noting the promotion
   - set `status: promoted`
   - update `last_touched`
10. Present the result with roadmap/project paths and the clearest next action.

---

## Promotion Reminder

Do not auto-promote, but do not make the user remember the command unaided.

Explicitly ask whether they want to promote the idea now when any of these are true:

- the idea status is `ready`
- a brief was just written
- the technical architecture now identifies real modules, dependencies, and an obvious first execution slice
- the user starts asking execution-shaped questions such as implementation order, milestones, repo structure, delivery slices, or what to build first

Use a short direct reminder such as:

- `Do you want me to promote this now with /idea <name> promote?`
- `If this is becoming a real multi-repo effort, I can promote it now and route through init-epic first.`

### Rules

- Promotion is explicit, not automatic.
- Promotion writes or proposes a roadmap row first.
- If the idea becomes a new multi-repo coordination effort, `init-epic` comes before `projects`.
- When the idea looks ready, explicitly remind the user that promotion is available.
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
- `spec.md` stays high-level. Code-level planning belongs in `/spec-new-feature` once repo grounding is required.
- Ideas can sit for months; the document should still be easy to re-enter.
