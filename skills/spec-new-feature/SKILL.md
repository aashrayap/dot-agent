---
name: spec-new-feature
description: Human-guided feature workflow — spec, direction Q&A, research, design, tasks, execute.
---

# Spec New Feature

## Composes With

- Parent: `idea`, `focus`, or `init-epic` when work needs code-grounded planning.
- Children: `ubiquitous-language` when repo terminology needs creation or refresh before planning; `excalidraw-diagram` when a feature plan needs a durable workflow, architecture, or before/after visual.
- Uses format from: `excalidraw-diagram` for human-facing planning and design visuals when useful.
- Reads state from: `docs/UBIQUITOUS_LANGUAGE.md` when present, idea `spec.md`/`plan.md`, roadmap rows, repo docs/code, and feature artifacts.
- Writes through: `docs/artifacts/<feature>/` for feature artifacts; returns PRs/pivots/follow-ups to roadmap rows, handoff docs, or PR descriptions.
- Hands off to: `focus` for roadmap follow-ups, `review` for PR review, or `daily-review` for day-end closure.
- Receives back from: `focus`, `review`, PR refs, and prior feature artifacts as curated workstream context.

Non-trivial feature work through spec, human direction Q&A, decontaminated research, design decisions, task breakdown, and optional execution.

This skill is the code-grounded planning bridge for mature ideas. `/idea` owns product/concept shaping and high-level technical architecture; `spec-new-feature` turns that into approved feature artifacts, human direction checkpoints, research, design, and executable tasks.

## Response Contract

- The universal response contract lives above this skill and applies to
  non-trivial runs when relevant.
- `spec-new-feature` implements that contract through `docs/artifacts/<feature>/`
  when the run creates multiple artifacts or needs durable review/resume.
- `00_summary.md` is a durable landing page for the artifact set. It is optional for tiny or simple runs, but expected for multi-artifact runs.
- When present, `00_summary.md` should orient the reader, link through `01_spec.md` to `05_tasks.md`, and embed or link a diagram when that helps.
- Keep the workflow intact and concise; do not add extra artifact layers unless they materially help the run.

## Artifact Contract

- `00_summary.md` — durable landing page for the artifact set when the run needs one
- `01_spec.md` — problem framing, users, acceptance criteria, boundaries, initial human direction
- `02_questions.md` — human direction questions plus approved research questions grouped by source
- `03_research.md` — decontaminated findings, patterns, flagged items, direction options, open questions
- `04_design.md` — chosen direction, design decisions, principles, file map, unresolved risks
- `05_tasks.md` — execution-ready task breakdown

When the feature involves workflow, architecture, state flow, or a before/after
model that a human needs to understand, add or update a companion Excalidraw
diagram under `docs/diagrams/` and link it from the relevant artifact. Do not
force a diagram for small mechanical changes or line-level fixes.

Each artifact tracks `status` in YAML frontmatter: `pending` → `draft` → `approved`/`complete`.

## Phase Detection

| Condition | Phase |
| --- | --- |
| `01_spec.md`: `draft` | L1 — Spec |
| `01_spec.md`: `approved`, `02_questions.md`: `pending` | L2 — Draft Questions |
| `02_questions.md`: `draft` | L2 — Questions Review |
| `02_questions.md`: `approved`, `03_research.md`: `pending` | L2 — Research |
| `03_research.md`: `complete`, `04_design.md`: `pending` | L2.5 — Direction Checkpoint |
| `04_design.md`: `draft` | L3 — Design Review |
| `04_design.md`: `approved`, `05_tasks.md`: `pending` | L4 — Tasks |
| `05_tasks.md`: `draft` | L4 — Task Review |
| `05_tasks.md`: `approved` | Execute |

## Invariants

- Before drafting `01_spec.md`, check for `docs/UBIQUITOUS_LANGUAGE.md` in the
  active repo. If present, read it and use its preferred terms in every feature
  artifact. If absent, continue without creating it unless the user invokes
  `ubiquitous-language`.
- Research decontamination: investigation receives only approved factual research questions, never the spec, feature name, desired solution, or `Human Direction` notes.
- Human direction is the center of the workflow. Use short back-and-forth Q&A to resolve goals, priorities, tradeoffs, and uncertain direction before committing to design, tasks, or execution.
- Questions must be specific and falsifiable.
- No code in `01_spec.md`, `02_questions.md`, `03_research.md`, or `04_design.md`.
- Code-level file paths, function names, schemas, API routes, and test commands belong in `05_tasks.md`, not in earlier artifacts, unless they are evidence gathered during research.
- The question list is a checkpoint — stop for approval before research unless the user explicitly asks to continue.
- Research-to-design is a checkpoint — present findings, options, and unresolved questions; get human direction before drafting `04_design.md` unless the user explicitly delegates the choice.
- Execution requires an approved design/tasks path plus an explicit human go-ahead.
- Keep uncertainty visible until explicitly resolved.
- Read `CLAUDE.md` and `README.md` files from the working directory before finalizing `04_design.md`.
- Preserve existing repo patterns over new abstractions unless the spec explicitly requires a break.

## From Idea

When invoked from an idea handoff:

1. Read the idea's `idea.md`, `brief.md` when present, `spec.md` when present, and `plan.md` when present.
2. Treat the idea docs as source material, not as approved implementation direction.
3. Convert product framing into `01_spec.md`:
   - users/personas
   - problem and value
   - acceptance criteria
   - explicit non-goals and boundaries
4. Convert high-level Technical Architecture into research questions and design risks, not code tasks.
5. If the idea is missing product clarity, stop and send the user back to `/idea <slug>` or `/idea <slug> brief`.
6. If technical unknowns remain, capture them in `02_questions.md` before design.

The idea handoff should reduce blank-page work, but it does not bypass approvals or research decontamination.

## Human Direction Loop

Use this loop before research, between research and design, during design when
tradeoffs are unresolved, and before execution:

1. State the decision or uncertainty in one sentence.
2. Ask the human 1-5 numbered questions or options that can be answered by
   number or short phrase.
3. Update the current artifact with `Human Direction`, `Resolved`, and
   `Still Open` notes.
4. Continue only when the next phase has enough direction to be defensible.

Default Q&A checkpoints:

- Before `02_questions.md` approval: confirm scope, non-goals, success shape,
  and what would make the work not worth doing.
- Before `03_research.md`: confirm the factual research questions are neutral
  and complete enough.
- Between `03_research.md` and `04_design.md`: show findings, list viable
  directions, call out tradeoffs, and ask the human to choose or delegate.
- Before `05_tasks.md`/execution: confirm delivery slice, risk tolerance, and
  whether implementation should start now.

If the user asks for uninterrupted planning, make conservative choices, record
assumptions in the artifact, and still stop before execution.

## Question Categories

Group questions in `02_questions.md` by source: `Human Direction`, `Codebase`,
`Docs`, `Patterns`, `External`, `Cross-Ref`.

Use `Human Direction` for questions the human must answer. Do not send that
section to decontaminated research agents or treat it as codebase evidence.

Good question: `Where is the retry policy defined, and which services currently use it?`

Bad question: `Can the current retry policy support our new bulk sync flow?`

## Research Output

For every question, capture: `Answer`, `Confidence`, `Evidence`, `Conflicts`, `Open`.

Merge into: `Flagged Items`, `Findings`, `Patterns Found`, `Core Docs Summary`, `Direction Options`, `Open Questions`.

Before design, convert the research into a short direction packet:

- what the evidence rules out
- viable options and tradeoffs
- recommended default, if any
- questions the human must answer before design

## Design And Plan Boundary

Use the idea-spec / idea-plan separation:

- `01_spec.md` and `04_design.md` explain what should exist and why.
- `04_design.md` starts from the chosen human direction, not from the researcher's preferred implementation.
- `05_tasks.md` is the first artifact that becomes code-specific.
- Tasks should name real files, functions, schemas, API routes, packages, migrations, and tests only after codebase research and design are complete.
- Each task should be independently handoffable to a coding agent.
- Acceptance criteria must be testable. Avoid placeholders like "works correctly."
- Include dependencies, sequencing, and parallelizable groups when they matter.
- Estimate effort in hours in `05_tasks.md` when the codebase is known; use rough sizes only before codebase grounding.

## Subagent Roles

Use portable roles when delegation is authorized:

- **Explorer** for decontaminated research, path verification, and factual
  codebase questions.
- **Worker / Implementor** for approved, file-scoped implementation tasks.
- **Gate / Verifier** after implementation waves to check changed files against
  task/spec intent.

Do not spawn subagents unless the user explicitly authorized delegation or
parallel agent work. When delegation is not authorized, keep the same role
separation in your own workflow: investigate first, implement second, verify
last.

## Execution Handoff

When `05_tasks.md` is approved:

1. Identify the smallest useful PR or delivery slice.
2. If delegation is authorized, dispatch file-disjoint tasks to Worker /
   Implementor roles and run a Gate / Verifier pass over the union of changed
   files before calling the wave complete.
3. Hand PRs, pivots, discarded approaches, and follow-ups back to `focus`, `review`, PR descriptions, or the relevant handoff doc.
4. If execution starts directly here, keep the final response tied to the approved task IDs and name the artifact or roadmap row that should receive follow-ups.
5. Do not create a parallel idea execution log. Durable delivery reality belongs in feature artifacts, PRs, roadmap rows, or handoff docs.
