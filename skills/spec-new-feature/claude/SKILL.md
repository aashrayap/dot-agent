---
name: spec-new-feature
description: Human-guided feature workflow for Claude Code — spec, direction Q&A, decontaminated research via subagents, design decisions, task breakdown, and wave-based execution.
disable-model-invocation: true
---

# Spec New Feature

## Composes With

- Parent: `idea`, `focus`, or `init-epic` when work needs code-grounded planning.
- Children: `excalidraw-diagram` when a feature plan needs a durable workflow, architecture, or before/after visual.
- Uses format from: `excalidraw-diagram` for human-facing planning and design visuals when useful.
- Reads state from: idea `spec.md`/`plan.md`, roadmap rows, repo docs/code, and feature artifacts.
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
- No code in L1–L3. Implementation details belong in L4 task specs only.
- Code-specific files, functions, schemas, API routes, packages, migrations, and verify commands belong in L4 task specs, not in earlier artifacts, unless they are evidence found during research.
- Read CLAUDE.md and README.md files before L3 — only from the working directory and its subdirectories. NEVER traverse parent directories to find these files.
- When the feature involves workflow, architecture, state flow, or a before/after
  model that a human needs to understand, add or update a companion Excalidraw
  diagram and link it from the relevant artifact.
- Questions must be specific and falsifiable.
- The question list is a checkpoint. Stop for approval before research unless the user clearly asks to continue without pausing.
- Research-to-design is a checkpoint. Present findings, viable directions, tradeoffs, and blocking questions; get human direction before drafting `04_design.md` unless the human explicitly delegates the choice.
- Execution requires approved tasks plus explicit human go-ahead.
- Keep uncertainty visible. Low-confidence findings, conflicting evidence, or unknown execution paths stay open until resolved.
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

If the input references an idea under `~/.dot-agent/state/ideas/<slug>/`, read `idea.md`, `brief.md`, `spec.md`, and `plan.md` when present. Convert the idea into users, acceptance criteria, boundaries, and open questions. If the idea is still missing product clarity, stop and route back to `/idea <slug>`.

---

## L2 — Investigate

**Owner:** AI with human checkpoints | **Output:** `02_questions.md`, `03_research.md`

### Draft Questions

Read `01_spec.md` and generate neutral, factual questions about the codebase. Strip all feature intent from research questions — they must be answerable without knowing what is being built.

Group questions into: `Human Direction`, `Codebase`, `Docs`, `Patterns`, `External`, `Cross-Ref`.

Good question: "How does the notifications service dispatch messages? What transports exist?"
Bad question: "Can the notifications service support our new bulk-alert feature?" ← leaks intent

Each question must be specific and falsifiable — answerable by reading 1-3 files with a concrete answer. If a question requires "read everything and summarize," split it.

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

Fill `03_research.md` with: `Flagged Items`, `Findings` (per-question Q&A with file paths), `Patterns Found`, `Core Docs Summary`, `Direction Options`, `Open Questions`.

**Confidence check** — For every finding: *"Do we know the exact path, or are we assuming?"* If a finding says "may exist", "should work", or "needs verification" — it is **unresolved**. Flag for further investigation or human input.

**Check gaps:**
- Spec gaps → loop to L1
- Unresolved questions needing human → pause and flag
- Uncertain execution paths → pause and flag to human
- Clean findings → prepare direction checkpoint before L3

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

The orchestrator performs decomposition directly — do NOT delegate to a subagent. The orchestrator has accumulated context through L1–L3 that cannot be faithfully serialized into a subagent prompt.

1. Read `04_design.md`, `01_spec.md`, `03_research.md`.
2. **Extract shared dependencies** — Identify utilities, mocks, helpers, or types that multiple tasks need. These go in Wave 1. Every downstream task must reference them by exact import path.
3. **Verify paths** — For uncertain file paths, dispatch a quick Explore subagent (`model: "sonnet"`) to confirm before including in a task spec.
4. Group work into parallel waves. Minimize waves respecting dependencies.
5. Write task specs. Each task gets:
   - **Implement:** files to create/modify, behavior to add
   - **Relevant Decisions:** inlined from `04_design.md`
   - **Interface Contract:** what downstream tasks consume (file paths, function signatures, types)
   - **Acceptance Criteria:** subset from `01_spec.md` mapped to this task
   - **Verify:** copy-pasteable commands
   - **Boundaries:** Always / Ask first / Never
   - **Effort:** hour estimate once the codebase is known
   - **Tracking ID:** stable task ID that can be cited from PRs, handoff docs, or roadmap follow-ups
6. **Self-containment test:** Could an agent implement each task with ONLY the task spec + CLAUDE.md? If not, inline missing context.
7. If a task needs an unresolved design decision → loop to L3.
8. Present to human. Execute only on explicit approval.

---

## Execute

After `05_tasks.md` approved, execute wave by wave:

Use portable roles: Worker / Implementor for file-scoped edits and Gate /
Verifier for post-wave validation. In Claude Code, these may map to named agents
such as Sushant's `task-implementor` and `gating-agent`; in Codex, use the
available worker/explorer roles only when delegation is authorized.

1. **Per wave** — One agent per task, parallel. Do NOT use `isolation: "worktree"`. Task decomposition guarantees no file conflicts, so worktrees add cherry-pick overhead without benefit.
2. **Agent prompt:**
   ```
   {Subagent Tooling Block}
   Implement task for feature "{name}".
   Task spec: {full task content from 05_tasks.md}
   Rules: Implement exactly what spec describes. Follow CLAUDE.md conventions. Run verify commands via Bash. Fix failures and re-verify. If spec doesn't cover something, STOP and report. Do NOT modify files outside task scope.
   ```
3. **Gate** — Run one Gate / Verifier pass over the union of changed files before calling the wave complete.
4. **Between waves** — Full type-check + lint + test across affected areas.
5. **Retries** — Agent fails after 2-3 attempts → escalate to human (usually a spec gap).
6. **Track** — Update checkboxes in `05_tasks.md`.
7. **Execution memory** — Hand PRs, pivots, discarded approaches, and follow-ups back to `focus`, `review`, PR descriptions, or the relevant handoff doc instead of creating a parallel idea execution log.

---
