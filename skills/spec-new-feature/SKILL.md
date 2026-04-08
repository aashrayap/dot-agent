---
name: spec-new-feature
description: Full feature workflow — spec, research, design, tasks, execute.
---

# Spec New Feature

Non-trivial feature work through spec, decontaminated research, design decisions, task breakdown, and optional execution.

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
- The question list is a checkpoint — stop for approval before research unless the user explicitly asks to continue.
- Keep uncertainty visible until explicitly resolved.
- Read `CLAUDE.md` and `README.md` files from the working directory before finalizing `04_design.md`.

## Question Categories

Group questions in `02_questions.md` by source: `Codebase`, `Docs`, `Patterns`, `External`, `Cross-Ref`.

Good question: `Where is the retry policy defined, and which services currently use it?`

Bad question: `Can the current retry policy support our new bulk sync flow?`

## Research Output

For every question, capture: `Answer`, `Confidence`, `Evidence`, `Conflicts`, `Open`.

Merge into: `Flagged Items`, `Findings`, `Patterns Found`, `Core Docs Summary`, `Open Questions`.
