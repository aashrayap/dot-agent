---
name: spec-new-feature
description: Human-guided feature workflow for Claude Code — spec, direction Q&A, decontaminated research via subagents, design decisions, task breakdown, and wave-based execution.
disable-model-invocation: true
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

Use this for non-trivial feature work that needs a spec, human direction Q&A, decontaminated research, design decisions, task breakdown, and optional execution.

This is also the code-grounded planning bridge for mature `/idea` work. Idea docs provide product and high-level architecture context; this workflow owns approved spec artifacts, human direction checkpoints, decontaminated research, design, code-specific tasks, and optional execution.

## Response Contract

- The universal response contract lives above this skill and applies to
  non-trivial runs when relevant.
- `spec-new-feature` implements that contract through `docs/artifacts/<feature>/`
  when the run creates multiple artifacts or needs durable review/resume.
- `00_summary.md` is the durable landing page for the artifact set when one is
  needed.

## Context

!`~/.claude/skills/spec-new-feature/scripts/new-feature-setup.sh $0`

User description: $ARGUMENTS

Read the reported feature directory and artifact statuses. Resume from the first artifact that is still `pending` or `draft`.

## Artifact Contract

- `00_summary.md` — durable landing page for the artifact set when the run needs one
- `01_spec.md` — problem framing, users, acceptance criteria, boundaries, initial human direction
- `02_questions.md` — human direction questions plus approved research questions grouped by source
- `03_research.md` — decontaminated findings, patterns, flagged items, direction options, open questions
- `04_design.md` — chosen direction, design decisions, principles, file map, unresolved risks
- `05_tasks.md` — execution-ready task breakdown

Track progress via `status` frontmatter: `pending` → `draft` → `approved`/`complete`.

## Principles

- **The spec is the product, the code is the build artifact.** Agents amplify both good and bad specifications.
- **Human direction before commitment.** Handle mechanical complexity autonomously, but use back-and-forth Q&A for goals, priorities, tradeoffs, risk tolerance, and direction before design, tasks, or execution.
- **Known complexity is fine; unknown paths must be flagged.** If you know exactly *what* to do but not *how to write the code*, that's fine — proceed. If you're not confident on the *exact path* to accomplish something (tooling, pipelines, infra), flag it for human confirmation before it becomes a task.
- **Research decontamination.** Investigation subagents must NOT know what the user wants to build. They receive only factual research questions — no feature name, no user stories, no desired outcomes, no `Human Direction` notes. This prevents confirmation bias: agents report what exists, not what supports the plan.

## Rules

- You are an orchestrator. NEVER read code or explore the codebase directly — dispatch subagents for ALL investigation, even follow-up questions from human feedback, verifying assumptions mid-conversation, or resolving disagreements. If the human challenges a decision and you need evidence, dispatch a subagent to gather it.
- Feature directory and templates are pre-created. Do NOT create them manually.
- On startup, read artifact files to determine current phase. Tell the human which phase you're starting and why.
- Before drafting `01_spec.md`, check for `docs/UBIQUITOUS_LANGUAGE.md` in the
  active repo. If present, read it and use its preferred terms in every feature
  artifact. If absent, continue without creating it unless the user invokes
  `ubiquitous-language`.
- No code in L1–L3. Implementation details belong in L4 task specs only.
- Code-specific files, functions, schemas, API routes, packages, migrations, and verify commands belong in L4 task specs, not in earlier artifacts, unless they are evidence found during research.
- Read CLAUDE.md and README.md files before L3 — only from the working directory and its subdirectories. NEVER traverse parent directories to find these files.
- When the feature involves workflow, architecture, state flow, or a before/after
  model that would be hard to follow in prose, consider `excalidraw-diagram`
  and link the result from the relevant artifact.
- Questions must be specific and falsifiable.
- The question list is a checkpoint. Stop for approval before research unless the user clearly asks to continue without pausing.
- Research-to-design is a checkpoint. Present findings, viable directions, tradeoffs, and blocking questions; get human direction before drafting `04_design.md` unless the human explicitly delegates the choice.
- Execution requires approved tasks plus explicit human go-ahead.
- Keep uncertainty visible. Low-confidence findings, conflicting evidence, or unknown execution paths stay open until resolved.
- Use `grill-me` at the research-to-design checkpoint or before tasking/execution when major branches or failure modes still feel unresolved. Record the resolved answers back into the active artifact instead of creating a new phase.
- **Tooling:** Include the Subagent Tooling Block (below) verbatim at the TOP of every subagent prompt that interacts with the filesystem. Omit it for pure-synthesis subagents whose inputs are inlined.
- **Model override:** All Explore subagents MUST use `model: "sonnet"`. Haiku does not reliably follow tool-usage instructions and falls back to Bash for file operations, causing permission spam.

### Subagent Tooling Block

Copy this into every subagent prompt as the first section:

```
MANDATORY TOOL USAGE — Read this first:
- Use the Glob tool to find files (NEVER bash find, ls, or shell globbing)
- Use the Grep tool to search file contents (NEVER bash grep, rg, or awk)
- Use the Read tool to read files (NEVER bash cat, head, tail, or sed)
- The Bash tool must ONLY be used for running build/test commands (tsc, bun test, etc.)
- WHY: Glob/Grep/Read require no permission approval and execute instantly. Bash file commands trigger permission prompts that block your execution.
```

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

---

## L1 — Articulate the Problem

**Owner:** Human + AI | **Output:** `01_spec.md`

1. **Listen** — Parse description. Identify core problem, users, outcomes.
2. **Probe** — Ask the human about: user stories with testable AC (Given/When/Then), edge cases, failure modes, unknowns, assumptions, boundaries, dependencies. The human knows the codebase — lean on them for context rather than scanning code.
3. **Direction Q&A** — Ask 1-5 numbered questions when scope, priority, risk tolerance, or success shape is ambiguous. Record answers under `Human Direction`.
4. **Draft** — Fill in `01_spec.md`.
5. **Devil's Advocate** — Every AC testable without human judgment? Third-party behaviors documented? Failure mode per external dep? Security explicit? Migration/backward-compat addressed?
6. **Gate** — Human must approve. Update `status: approved`. Do NOT proceed to L2 until approved.

If the input references an idea under `~/.dot-agent/state/ideas/<slug>/`, read
the available idea docs, treat them as source material, move product framing
into `01_spec.md`, move technical unknowns into `02_questions.md`, and route
back to `/idea <slug>` if product clarity is still weak.

---

## L2 — Investigate

**Owner:** AI with human checkpoints | **Output:** `02_questions.md`, `03_research.md`

### Draft Questions

Read `01_spec.md` and generate neutral, factual questions about the codebase.
Group them into `Human Direction`, `Codebase`, `Docs`, `Patterns`,
`External`, and `Cross-Ref`. `Human Direction` is human-only and never goes to
decontaminated research. Keep questions narrow enough to answer from a small
set of files or docs.

Stop for approval before proceeding to research. Use the checkpoint to ask whether the human wants to add, remove, or reframe questions before decontaminated research starts.

### Dispatch Research

**⚠️ DECONTAMINATION RULE:** Investigation subagents must NOT receive the spec, feature name, user stories, desired outcomes, or `Human Direction` notes. They receive only assigned factual research questions from `02_questions.md` and their focus area.

Dispatch parallel subagents:
- **Codebase Investigation** — one per area, `subagent_type: "Explore"`, `model: "sonnet"`
- **External Research** — `subagent_type: "general-purpose"` for third-party APIs/services
- If the feature depends on generated code or build tooling, dispatch a dedicated subagent for the generation/build pipeline.

#### Codebase Investigation Subagent

```
{Subagent Tooling Block}

Answer the following questions about the codebase. Focus area: {service/directory}

Questions (from 02_questions.md):
{paste only the assigned question numbers and text}

For each question, provide:
- **Answer**: direct answer in 1-3 sentences
- **Evidence**: file paths with line numbers
- **Confidence**: high | medium | low
- **Conflicts**: contradictions found, or "none"
- **Open**: what couldn't be determined, or "none"

Additionally report:
- **Patterns Found**: conventions/patterns observed with file references
- **Surprises**: anything unexpected or noteworthy

Rules: Include file paths for every claim. Distinguish canonical vs deprecated patterns. Flag surprises prominently. Do NOT suggest implementations — just report what exists. If you cannot fully verify how something works, explicitly say so — do NOT report it as resolved. Read README.md files in relevant directories.
```

#### External Research Subagent

```
{Subagent Tooling Block}

Answer the following questions about {API/service name}:
{paste only the assigned question numbers and text from 02_questions.md}

Find: current docs, endpoints, auth, rate limits, request/response shapes, SDK compatibility, gotchas.

For each question, provide:
- **Answer**: direct answer in 1-3 sentences
- **Evidence**: documentation URLs or source references
- **Confidence**: high | medium | low
- **Conflicts**: contradictions found, or "none"
- **Open**: what couldn't be determined, or "none"

Rules: Only verified info from official docs. Flag UNVERIFIED claims. Include source URLs. Do NOT suggest how to use the API for any particular purpose — just document what it does and how it works.
```

### Synthesize

Fill `03_research.md` with `Flagged Items`, `Findings`, `Patterns Found`,
`Core Docs Summary`, `Direction Options`, and `Open Questions`. Keep low
confidence items unresolved instead of smoothing them into decisions.

### Direction Checkpoint

Before drafting `04_design.md`, present a short direction packet:

- what the evidence rules out
- viable directions and tradeoffs
- recommended default, if any
- numbered questions for the human

Update `03_research.md` with the human answer under `Human Direction` or
`Direction Options`. Proceed to L3 only after the human chooses a direction or
explicitly delegates the choice.

---

## L3 — Design Decisions

**Owner:** Human at uncertainty, AI otherwise | **Output:** `04_design.md`

1. **Start from Direction** — Read the direction checkpoint answer first. If it is missing, stop and ask for it.
2. **Gather Principles** — Dispatch an Explore subagent (`model: "sonnet"`) to find and read all CLAUDE.md and README.md files within the working directory and its subdirectories. Return relevant principles, conventions, and documented workflows.
3. **Draft Decisions** — For each design choice: Chosen Direction, Finding, Options, Decision, Principle, Scope (affected files/areas). **Every file reference MUST use the full path from the repo root.** Downstream agents cannot resolve ambiguous paths.
4. **Human Checkpoint** — Present decisions. Human intervenes when: principles conflict, no precedent exists, decision forces spec change (→ loop L1), or tradeoffs need preference. **If the human disagrees or raises questions needing codebase evidence, dispatch a subagent to investigate before responding.**
5. **Technical Design** — Synthesize approach, data model changes, API contracts, file-level change map. Keep unresolved risks visible.
6. **Gate** — Human must approve. Update `status: approved`.

---

## L4 — Decompose into Tasks

**Owner:** AI (orchestrator directly) | **Output:** `05_tasks.md`

The orchestrator performs decomposition directly. Do not delegate this phase.

1. Read `04_design.md`, `01_spec.md`, `03_research.md`.
2. Extract shared dependencies first.
3. Verify uncertain file paths before writing them into tasks.
4. Group work into parallel-safe waves.
5. Make each task self-contained: exact files, relevant decisions, acceptance
   criteria, verify commands, boundaries, effort, and stable task ID.
6. If a task depends on an unresolved design question, loop back to L3.
7. Present to the human. Execute only on explicit approval.

---

## Execute

After `05_tasks.md` approved, execute wave by wave:

Use portable roles: Worker / Implementor for file-scoped edits and Gate /
Verifier for post-wave validation. In Claude Code, these may map to named agents
such as Sushant's `task-implementor` and `gating-agent`; in Codex, use the
available worker/explorer roles only when delegation is authorized.

1. **Per wave** — One agent per task, parallel. Do not use worktrees for
   file-disjoint tasks.
2. **Agent prompt:**
   ```
   {Subagent Tooling Block}
   Implement task for feature "{name}".
   Task spec: {full task content from 05_tasks.md}
   Rules: Implement exactly what spec describes. Follow CLAUDE.md conventions. Run verify commands via Bash. Fix failures and re-verify. If spec doesn't cover something, STOP and report. Do NOT modify files outside task scope.
   ```
3. **Gate** — Run one verifier pass over the changed set before calling the
   wave complete.
4. **Between waves** — Run the shared checks for affected areas.
5. **Retries** — After a few failed attempts, escalate to the human.
6. **Track** — Update `05_tasks.md`.
7. **Execution memory** — Hand PRs, pivots, and follow-ups back to `focus`,
   `review`, PR text, or the relevant handoff doc instead of creating a
   parallel execution log.

---
