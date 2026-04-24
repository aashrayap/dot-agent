---
name: spec-new-feature
description: Plan and optionally execute non-trivial feature work using human direction Q&A, approved research questions, decontaminated research, design decisions, task breakdown, and execution.
---

# Spec New Feature

## Composes With

- Parent: `idea`, `focus`, or `init-epic` when work needs code-grounded planning.
- Children: `ubiquitous-language` when repo terminology needs creation or refresh before planning; `grill-me` for pressure-test checkpoints when research or design still has unresolved branches; `excalidraw-diagram` when a feature plan needs a durable workflow, architecture, or before/after visual.
- Uses format from: `excalidraw-diagram` for human-facing planning and design visuals when useful.
- Reads state from: `docs/UBIQUITOUS_LANGUAGE.md` when present, idea `spec.md`/`plan.md`, roadmap rows, repo docs/code, and feature artifacts.
- Writes through: `docs/artifacts/<feature>/` for feature artifacts; returns PRs/pivots/follow-ups to roadmap rows, handoff docs, or PR descriptions.
- Hands off to: `focus` for roadmap follow-ups, `review` for PR review, or `daily-review` for day-end closure.
- Receives back from: `focus`, `review`, PR refs, and prior feature artifacts as curated workstream context.

Use this for new features, significant behavior changes, or multi-file work where the requirements and direction need to be shaped with the human before implementation.

This is also the code-grounded planning bridge for mature `/idea` work. Idea docs provide product and high-level architecture context; this workflow owns approved spec artifacts, human direction checkpoints, decontaminated research, design, code-specific tasks, and optional execution.

## Response Contract

- The universal response contract lives above this skill and applies to
  non-trivial runs when relevant.
- `spec-new-feature` implements that contract through `docs/artifacts/<feature>/`
  when the run creates multiple artifacts or needs durable review/resume.
- `00_summary.md` is the durable landing page for the artifact set when one is
  needed.

## Quick Start

Run `scripts/init-feature-artifacts.sh <feature-slug>` first. It creates or resumes the core phase artifacts:

- `docs/artifacts/<feature>/01_spec.md`
- `docs/artifacts/<feature>/02_questions.md`
- `docs/artifacts/<feature>/03_research.md`
- `docs/artifacts/<feature>/04_design.md`
- `docs/artifacts/<feature>/05_tasks.md`

If the feature already exists, resume from the first incomplete phase instead of recreating artifacts.

## Rules

- Before drafting `01_spec.md`, check for `docs/UBIQUITOUS_LANGUAGE.md` in the
  active repo. If present, read it and use its preferred terms in every feature
  artifact. If absent, continue without creating it unless the user invokes
  `ubiquitous-language`.
- Do not explore the codebase before drafting the initial research questions.
- Use human Q&A to resolve direction before research, between research and design, and before execution.
- Questions must be specific and falsifiable.
- The question list is a checkpoint. Get explicit approval before research unless the user clearly asks to continue without pausing.
- Research is for discovering current reality, not defending a preferred solution.
- Keep research decontaminated. During the research phase, answer only the factual sections of `02_questions.md`; keep `Human Direction`, the spec, and desired solution out of research prompts.
- Separate findings by source: `codebase`, `docs`, `patterns`, `external`, and `cross-ref`.
- Every finding needs evidence and a confidence level.
- Keep unresolved items unresolved. Do not convert uncertainty into decisions.
- Prefer local docs and code first. Use external docs only when needed and cite them.
- Default checkpoints: ask for approval on the question list before research and on the design before execution. If the user explicitly asks for uninterrupted planning, continue and record assumptions clearly.
- Research-to-design is a checkpoint: present findings, viable directions, tradeoffs, and blocking questions; get human direction before drafting `04_design.md` unless the user explicitly delegates the choice.
- Execution requires approved tasks plus explicit human go-ahead.
- Use `grill-me` at the research-to-design checkpoint or before tasking/execution when major branches or failure modes still feel unresolved. Record the resolved answers back into the active artifact instead of creating a new phase.
- Only parallelize research with subagents if the user explicitly asks for delegated or parallel agent work.
- Code-specific files, function names, schemas, API routes, packages, migrations, and verify commands belong in `05_tasks.md`, not in earlier artifacts, unless they are evidence found during research.
- When this starts from an idea handoff, read the available idea docs, treat
  them as source material, move product framing into `01_spec.md`, move
  technical unknowns into `02_questions.md`, and route back to `/idea` if
  product clarity is still weak.
- When the feature involves workflow, architecture, state flow, or a before/after
  model that would be hard to follow in prose, consider `excalidraw-diagram`
  and link the result from the relevant artifact.

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
- human direction: priorities, tradeoffs, assumptions, and open choices

Keep this focused on the problem. Do not turn it into implementation notes.

If the input references an idea under `~/.dot-agent/state/ideas/<slug>/`, also read the matching `idea.md`, `brief.md`, `spec.md`, and `plan.md` when present. Convert the idea into users, acceptance criteria, boundaries, and open questions. If the idea is still missing product clarity, stop and route back to `/idea <slug>`.

### 3. Draft `02_questions.md`

Write factual, decontaminated questions that must be answered before design.
Group them into `Human Direction`, `Codebase`, `Docs`, `Patterns`,
`External`, and `Cross-Ref`. `Human Direction` is human-only and never goes to
research. Keep questions narrow enough to answer from a small set of files or
docs.

Pause for approval after drafting the questions unless the user asked you not to.

### 4. Produce `03_research.md`

Research from the approved factual sections of the questions artifact. Do not
send `Human Direction` notes into decontaminated research.

For each question, capture `answer`, `evidence`, `confidence`, `conflicts`,
and `open items`. Merge that into `Flagged Items`, `Findings`,
`Patterns Found`, `Core Docs Summary`, `Direction Options`, and
`Open Questions`. Keep low-confidence items unresolved. Do not suggest
implementations in this phase.

After research, pause with a short direction packet: what the evidence rules
out, what options remain, the default recommendation if any, and what still
needs a human choice.

Record the human answer in `03_research.md` or `04_design.md`. Continue to design only after the direction is clear or explicitly delegated.

### 5. Draft `04_design.md`

Start from the chosen human direction.

For each important design choice, record:

- chosen direction
- decision
- options considered
- rationale
- affected files or areas
- risks still open

Also record the relevant repo principles or conventions that shaped the choice.

If the design still depends on unknowns, stop and ask concise numbered questions.

### 6. Draft `05_tasks.md`

Break the work into file-scoped, self-contained tasks with exact file targets,
dependencies, acceptance criteria, verify commands, boundaries, effort
estimates when possible, and stable task IDs.

### 7. Optional Execution

If the user asks to execute:

- choose the smallest useful delivery slice
- follow task dependency order
- parallelize only file-disjoint work
- verify after each task or wave
- stop on design gaps or direction gaps
- hand follow-ups back to `focus`, `review`, PR text, or the relevant handoff
  doc instead of creating a parallel execution log

## Non-Goals

- browser QA
- fake multi-agent orchestration
- solving design ambiguity by guessing
