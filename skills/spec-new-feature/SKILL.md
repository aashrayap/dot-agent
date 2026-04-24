---
name: spec-new-feature
description: Human-guided feature workflow — spec, direction Q&A, research, design, tasks, execute.
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
model that would be hard to follow in prose, consider `excalidraw-diagram` and
link the result from the relevant artifact. Do not force a companion diagram
for small mechanical changes or line-level fixes.

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

If this starts from `/idea <slug>`:

- read available `idea.md`, `brief.md`, `spec.md`, and `plan.md`
- treat them as source material, not approved implementation direction
- move product framing into `01_spec.md`
- move technical unknowns into `02_questions.md`
- if product framing is still weak, send the user back to `/idea <slug>` or
  `/idea <slug> brief`

## Human Direction Loop

Use short Q&A at phase boundaries:

1. State the uncertainty in one sentence.
2. Ask 1-5 numbered questions.
3. Record `Human Direction`, `Resolved`, and `Still Open` in the current
   artifact.
4. Continue only when the next phase is defensible.

Default checkpoints: before research approval, between research and design, and
before tasks or execution. Use `grill-me` when branches still feel soft. If the
user wants uninterrupted planning, record assumptions and still stop before
execution.

## Questions And Research

In `02_questions.md`, group factual questions by `Human Direction`,
`Codebase`, `Docs`, `Patterns`, `External`, and `Cross-Ref`. `Human Direction`
is human-only and never goes to decontaminated research.

For each researched question, capture `Answer`, `Confidence`, `Evidence`,
`Conflicts`, and `Open`. Roll that into `Flagged Items`, `Findings`,
`Patterns Found`, `Core Docs Summary`, `Direction Options`, and
`Open Questions`.

Before design, return a short direction packet: what the evidence rules out,
what options remain, the default recommendation if any, and what still needs a
human call.

## Design And Plan Boundary

- `01_spec.md` and `04_design.md` explain what and why.
- `05_tasks.md` is the first code-specific artifact.
- Do not name real files, interfaces, migrations, or verify commands until
  research and design are done.
- Each task must be independently handoffable, testable, and sequenced when
  dependencies matter.
- Add effort estimates when the codebase is known.

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

- choose the smallest useful delivery slice
- if delegation is allowed, split only file-disjoint work and run one verifier
  pass over the changed set
- send follow-ups to `focus`, `review`, PR text, or handoff docs
- keep responses tied to task IDs and the owning artifact or roadmap row
- do not create a parallel execution log
