---
name: spec-new-feature
description: Plan and optionally execute non-trivial feature work using an artifact-driven workflow with spec, approved research questions, decontaminated research, design decisions, task breakdown, and execution.
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

Use this for new features, significant behavior changes, or multi-file work where the requirements need to be shaped before implementation.

This is also the code-grounded planning bridge for mature `/idea` work. Idea docs provide product and high-level architecture context; this workflow owns approved spec artifacts, decontaminated research, design, code-specific tasks, and optional execution.

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
- The question list is a checkpoint. Get explicit approval before research unless the user clearly asks to continue without pausing.
- Research is for discovering current reality, not defending a preferred solution.
- Keep research decontaminated. During the research phase, treat `02_questions.md` as the primary input and avoid pulling in the spec or desired solution while answering the questions.
- Separate findings by source: `codebase`, `docs`, `patterns`, `external`, and `cross-ref`.
- Every finding needs evidence and a confidence level.
- Keep unresolved items unresolved. Do not convert uncertainty into decisions.
- Prefer local docs and code first. Use external docs only when needed and cite them.
- Default checkpoints: ask for approval on the question list before research and on the design before execution. If the user explicitly asks for uninterrupted planning, continue and record assumptions clearly.
- Only parallelize research with subagents if the user explicitly asks for delegated or parallel agent work.
- Code-specific files, function names, schemas, API routes, packages, migrations, and verify commands belong in `05_tasks.md`, not in earlier artifacts, unless they are evidence found during research.
- When this starts from an idea handoff, preserve the product framing but do not treat the idea's technical architecture as implementation authority until research/design verifies it.

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

If the input references an idea under `~/.dot-agent/state/ideas/<slug>/`, also read the matching `idea.md`, `brief.md`, `spec.md`, and `plan.md` when present. Convert the idea into users, acceptance criteria, boundaries, and open questions. If the idea is still missing product clarity, stop and route back to `/idea <slug>`.

### 3. Draft `02_questions.md`

Write factual questions that must be answered before design:

- existing code paths
- data model constraints
- documented conventions
- relevant patterns
- external API or library questions
- questions that depend on combining multiple findings (`cross-ref`)

Bad question: "Can we build this quickly?"

Good question: "Where is the existing job retry policy defined, and which services already consume it?"

Organize the file into:

- `Codebase`
- `Docs`
- `Patterns`
- `External`
- `Cross-Ref`

Pause for approval after drafting the questions unless the user asked you not to.

### 4. Produce `03_research.md`

Research from the approved questions artifact.

Work question-by-question. For each question, capture:

- answer
- evidence
- confidence
- conflicts
- open items

Then merge the results into:

- `Flagged Items` for low-confidence or conflicting findings
- `Findings` for per-question answers
- `Patterns Found`
- `Core Docs Summary`
- `Open Questions`

Do not suggest implementations in this phase.

### 5. Draft `04_design.md`

For each important design choice, record:

- decision
- options considered
- rationale
- affected files or areas
- risks still open

Also record the relevant repo principles or conventions that shaped the choice.

If the design still depends on unknowns, stop and surface them.

### 6. Draft `05_tasks.md`

Break the work into file-scoped tasks with:

- exact files to create or modify
- dependency order
- parallel-safe groupings
- acceptance criteria
- verify commands
- boundaries and out-of-scope notes
- effort estimates in hours when the codebase is known
- task IDs that can be referenced from `projects/execution.md`

Tasks should be self-contained enough to execute without re-reading the entire design.

### 7. Optional Execution

If the user asks to execute:

- follow task dependency order
- parallelize only file-disjoint tasks
- run the verify commands after each task or task wave
- stop if execution uncovers a design gap that the plan did not resolve
- if this belongs to a tracked project, hand PRs, pivots, discarded approaches, and follow-ups back to `projects/execution.md` instead of creating a parallel idea execution log

## Non-Goals

- browser QA
- fake multi-agent orchestration
- solving design ambiguity by guessing
