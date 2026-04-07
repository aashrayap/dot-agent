---
name: spec-new-feature
description: Plan and optionally execute non-trivial feature work using an artifact-driven workflow with spec, research questions, decontaminated research, design decisions, task breakdown, and execution.
---

# Spec New Feature

Use this for new features, significant behavior changes, or multi-file work where the requirements need to be shaped before implementation.

## Quick Start

Run `scripts/init-feature-artifacts.sh <feature-slug>` first. It creates or resumes:

- `docs/artifacts/<feature>/01_spec.md`
- `docs/artifacts/<feature>/02_questions.md`
- `docs/artifacts/<feature>/03_research.md`
- `docs/artifacts/<feature>/04_design.md`
- `docs/artifacts/<feature>/05_tasks.md`

If the feature already exists, resume from the first incomplete phase instead of recreating artifacts.

## Rules

- Do not explore the codebase before drafting the initial research questions.
- Questions must be specific and falsifiable.
- Research is for discovering current reality, not defending a preferred solution.
- Treat `02_questions.md` as the primary input to the research phase.
- Separate findings by source: `codebase`, `docs`, `patterns`, `external`.
- Every finding needs evidence and a confidence level.
- Keep unresolved items unresolved. Do not convert uncertainty into decisions.
- Prefer local docs and code first. Use external docs only when needed and cite them.
- Default checkpoints: ask for approval on the question list before research and on the design before execution. If the user explicitly asks for uninterrupted planning, continue and record assumptions clearly.

## Workflow

### 1. Bootstrap

- Run `scripts/init-feature-artifacts.sh <feature-slug>`.
- Read the reported mode and file statuses.
- If resuming, continue from the first file that is still `pending` or `draft`.

### 2. Draft `01_spec.md`

Capture:

- goal and scope
- users and workflows
- acceptance criteria
- boundaries and non-goals
- risks, migrations, and external dependencies

Keep this focused on the problem. Do not turn it into implementation notes.

### 3. Draft `02_questions.md`

Write factual questions that must be answered before design:

- existing code paths
- data model constraints
- documented conventions
- relevant patterns
- external API or library questions

Bad question: "Can we build this quickly?"

Good question: "Where is the existing job retry policy defined, and which services already consume it?"

### 4. Produce `03_research.md`

Research from the approved questions artifact.

For each question, record:

- answer
- evidence
- confidence
- conflicts
- open items

Do not suggest implementations in this phase.

### 5. Draft `04_design.md`

For each important design choice, record:

- decision
- options considered
- rationale
- affected files or areas
- risks still open

If the design still depends on unknowns, stop and surface them.

### 6. Draft `05_tasks.md`

Break the work into file-scoped tasks with:

- exact files to create or modify
- dependency order
- parallel-safe groupings
- acceptance criteria
- verify commands
- boundaries and out-of-scope notes

Tasks should be self-contained enough to execute without re-reading the entire design.

### 7. Optional Execution

If the user asks to execute:

- follow task dependency order
- parallelize only file-disjoint tasks
- run the verify commands after each task or task wave
- stop if execution uncovers a design gap that the plan did not resolve

## Non-Goals

- browser QA
- fake multi-agent orchestration
- solving design ambiguity by guessing
