---
name: spec-new-feature
description: Full feature workflow for Claude Code with artifact bootstrap, approved research questions, decontaminated investigation, design decisions, task breakdown, and execution.
disable-model-invocation: true
---

# Spec New Feature

Use this for non-trivial feature work that needs a spec, decontaminated research, design decisions, task breakdown, and optional execution.

## Context

!`~/.claude/skills/spec-new-feature/scripts/new-feature-setup.sh $0`

User description: $ARGUMENTS

Read the reported feature directory and artifact statuses. Resume from the first artifact that is still `pending` or `draft`.

## Artifact Contract

- `01_spec.md` — problem framing, users, acceptance criteria, boundaries
- `02_questions.md` — approved research questions grouped by source
- `03_research.md` — decontaminated findings, patterns, flagged items, open questions
- `04_design.md` — design decisions, principles, file map, unresolved risks
- `05_tasks.md` — execution-ready task breakdown

## Rules

- Do not explore the codebase before drafting `02_questions.md`.
- Questions must be specific and falsifiable.
- The question list is a checkpoint. Stop for approval before research unless the user clearly asks to continue without pausing.
- Keep research decontaminated. Investigation windows should receive only the approved questions and their assigned focus, never the spec, feature name, or desired solution.
- No code in `01_spec.md`, `02_questions.md`, `03_research.md`, or `04_design.md`.
- Read `CLAUDE.md` and `README.md` files from the working directory and its subdirectories before finalizing `04_design.md`.
- Keep uncertainty visible. Low-confidence findings, conflicting evidence, or unknown execution paths stay open until resolved.
- Use fresh research windows when needed. Each research window should own a narrow set of questions and return evidence, confidence, conflicts, and open items.

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

## L1 — Draft `01_spec.md`

1. Capture the goal, users, workflows, acceptance criteria, boundaries, risks, and dependencies.
2. Keep it problem-first. Do not turn it into implementation notes.
3. Challenge ambiguity before moving on: unclear success criteria, missing constraints, external unknowns, migration risks.
4. Stop for approval. Update status to `approved`.

## L2 — Draft `02_questions.md`

1. Read `01_spec.md` and write neutral questions that can be answered without knowing the desired solution.
2. Group questions into `Codebase`, `Docs`, `Patterns`, `External`, and `Cross-Ref`.
3. Keep questions narrow enough to answer with targeted reads.
4. Ask for approval. Update status to `approved` before research unless the user explicitly asks to keep going.

Good question: `Where is the retry policy defined, and which services currently use it?`

Bad question: `Can the current retry policy support our new bulk sync flow?`

## L2 — Produce `03_research.md`

1. Treat `02_questions.md` as the only research input.
2. Classify each question to one source type:
   - `codebase`
   - `docs`
   - `patterns`
   - `external`
   - `cross-ref`
3. Use separate research windows when helpful, but keep each one decontaminated and narrowly scoped.
4. For every question, capture:
   - `Answer`
   - `Confidence`
   - `Evidence`
   - `Conflicts`
   - `Open`
5. Merge the outputs into:
   - `Flagged Items`
   - `Findings`
   - `Patterns Found`
   - `Core Docs Summary`
   - `Open Questions`
6. Mark `03_research.md` as `complete` only when the unknowns are explicit.

## L3 — Draft `04_design.md`

1. Combine the approved spec, the research findings, and the repo’s documented principles.
2. For each design choice, record:
   - decision
   - options considered
   - rationale
   - relevant principles
   - affected files or areas
3. Add a concise file map and keep unresolved risks visible.
4. Stop for approval. Update status to `approved`.

## L4 — Draft `05_tasks.md`

1. Break the design into execution-ready tasks with exact files, dependencies, verify commands, and acceptance criteria.
2. Group parallel-safe work into waves.
3. Inline enough context that an implementation window can execute the task without re-reading the whole design.
4. Stop for approval. Update status to `approved`.

## Execute

If the user asks to execute:

1. Follow task dependencies and only parallelize file-disjoint work.
2. Run verify commands after each task or wave.
3. Stop if implementation reveals a design gap the plan did not resolve.

---
