---
name: spec-new-feature
description: Full feature workflow — spec, research, design, tasks, execute.
---

# Spec New Feature

## Composes With

- Parent: `idea` or `projects` when work needs code-grounded planning.
- Children: none.
- Uses format from: none.
- Reads state from: idea `spec.md`/`plan.md`, thin project `Current Slice`, repo docs/code, and feature artifacts.
- Writes through: `docs/artifacts/<feature>/` for feature artifacts; returns PRs/pivots/follow-ups to `projects`.
- Hands off to: `projects` after execution or when durable memory is needed.
- Receives back from: `projects` as curated workstream context.

Non-trivial feature work through spec, decontaminated research, design decisions, task breakdown, and optional execution.

This skill is the code-grounded planning bridge for mature ideas. `/idea` owns product/concept shaping and high-level technical architecture; `spec-new-feature` turns that into approved feature artifacts, research, design, and executable tasks.

## Artifact Contract

- `01_spec.md` — problem framing, users, acceptance criteria, boundaries
- `02_questions.md` — approved research questions grouped by source
- `03_research.md` — decontaminated findings, patterns, flagged items, open questions
- `04_design.md` — design decisions, principles, file map, unresolved risks
- `05_tasks.md` — execution-ready task breakdown

Each artifact tracks `status` in YAML frontmatter: `pending` → `draft` → `approved`/`complete`.

## Phase Detection

| Condition | Phase |
| --- | --- |
| `01_spec.md`: `draft` | L1 — Spec |
| `01_spec.md`: `approved`, `02_questions.md`: `pending` | L2 — Draft Questions |
| `02_questions.md`: `draft` | L2 — Questions Review |
| `02_questions.md`: `approved`, `03_research.md`: `pending` | L2 — Research |
| `03_research.md`: `complete`, `04_design.md`: `pending` | L3 — Design |
| `04_design.md`: `draft` | L3 — Design Review |
| `04_design.md`: `approved`, `05_tasks.md`: `pending` | L4 — Tasks |
| `05_tasks.md`: `draft` | L4 — Task Review |
| `05_tasks.md`: `approved` | Execute |

## Invariants

- Research decontamination: investigation receives only the approved questions, never the spec, feature name, or desired solution.
- Questions must be specific and falsifiable.
- No code in `01_spec.md`, `02_questions.md`, `03_research.md`, or `04_design.md`.
- Code-level file paths, function names, schemas, API routes, and test commands belong in `05_tasks.md`, not in earlier artifacts, unless they are evidence gathered during research.
- The question list is a checkpoint — stop for approval before research unless the user explicitly asks to continue.
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

## Question Categories

Group questions in `02_questions.md` by source: `Codebase`, `Docs`, `Patterns`, `External`, `Cross-Ref`.

Good question: `Where is the retry policy defined, and which services currently use it?`

Bad question: `Can the current retry policy support our new bulk sync flow?`

## Research Output

For every question, capture: `Answer`, `Confidence`, `Evidence`, `Conflicts`, `Open`.

Merge into: `Flagged Items`, `Findings`, `Patterns Found`, `Core Docs Summary`, `Open Questions`.

## Design And Plan Boundary

Use the idea-spec / idea-plan separation:

- `01_spec.md` and `04_design.md` explain what should exist and why.
- `05_tasks.md` is the first artifact that becomes code-specific.
- Tasks should name real files, functions, schemas, API routes, packages, migrations, and tests only after codebase research and design are complete.
- Each task should be independently handoffable to a coding agent.
- Acceptance criteria must be testable. Avoid placeholders like "works correctly."
- Include dependencies, sequencing, and parallelizable groups when they matter.
- Estimate effort in hours in `05_tasks.md` when the codebase is known; use rough sizes only before codebase grounding.

## Execution Handoff

When `05_tasks.md` is approved:

1. Identify the smallest useful PR or delivery slice.
2. If the work belongs to a tracked project, hand it back to `projects <slug>` so execution memory owns PRs, pivots, and follow-ups.
3. If execution starts directly here, keep the final response tied to the approved task IDs and tell the user what should be logged in `projects/execution.md` afterward.
4. Do not create a parallel idea execution log. Durable delivery reality belongs in `projects`.
