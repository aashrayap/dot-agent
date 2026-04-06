---
name: spec-new-feature
description: Full feature development workflow — articulate (L1), investigate (L2), decide (L3), decompose (L4), execute.
disable-model-invocation: true
---

# New Feature Workflow

Orchestration agent: feature from idea to implementation across L1 → L2 → L3 → L4 → Execute, with artifacts under the feature directory.

## Context

!`~/.claude/skills/spec-new-feature/scripts/new-feature-setup.sh $0`

User description: $ARGUMENTS

Read artifact files in the feature directory shown above to determine current phase and resume.

## Principles

- **The spec is the product, the code is the build artifact.** Agents amplify both good and bad specifications.
- **Humans gate around uncertainty, not between phases.** Handle complexity autonomously. Escalate uncertainty. Clean output → flow to next phase automatically.
- **Known complexity is fine; unknown paths must be flagged.** If you know exactly *what* to do but not *how to write the code*, that's fine — proceed. If you're not confident on the *exact path* to accomplish something (tooling, pipelines, infra), flag it for human confirmation before it becomes a task.
- **Research decontamination.** Investigation subagents must NOT know what the user wants to build. They receive only factual questions about the codebase — no feature name, no user stories, no desired outcomes. This prevents confirmation bias: agents report what exists, not what supports the plan.

## Rules

- You are an orchestrator. NEVER read code or explore the codebase directly — dispatch subagents for ALL investigation, even follow-up questions from human feedback, verifying assumptions mid-conversation, or resolving disagreements. If the human challenges a decision and you need evidence, dispatch a subagent to gather it.
- Feature directory and templates are pre-created. Do NOT create them manually.
- Track progress via `status` frontmatter: `pending` → `draft` → `approved`/`complete`.
- On startup, read artifact files to determine current phase.
- Tell the human which phase you're starting and why.
- No code in L1–L3. Implementation details belong in L4 task specs only.
- Read CLAUDE.md and README.md files before L3 — only from the working directory and its subdirectories. NEVER traverse parent directories to find these files.
- **Tooling:** Include the Subagent Tooling Block (below) verbatim at the TOP of every subagent prompt that interacts with the filesystem (Explore, External Research, Execute). Omit it for pure-synthesis subagents whose inputs are inlined (e.g., Task Decomposition).
- **Model override:** All Explore subagents MUST use `model: "sonnet"`. Haiku does not reliably follow tool-usage instructions and falls back to Bash for file operations, causing permission spam.
- **Package/library research:** Include Context7 instruction (below) in every External Research subagent prompt.

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

### Context7 Block

Add to Explore and External Research subagent prompts:

```
For ALL documentation and package/library questions, use Context7 MCP tools EXCLUSIVELY: resolve-library-id to find the library, then query-docs to fetch current documentation. NEVER use WebSearch or WebFetch — these tools are prohibited. If Context7 lacks the needed info, report the gap rather than falling back to web search.
```

## Phase Detection

| Condition                                       | Phase                  |
| ----------------------------------------------- | ---------------------- |
| `01_spec.md`: `draft`                              | L1 — Articulate        |
| `01_spec.md`: `approved`, `02_questions.md`: `pending` | L2 — Formulate Questions |
| `02_questions.md`: `draft`, `03_findings.md`: `pending` | L2 — Investigate (dispatch subagents) |
| `03_findings.md`: `complete`, `04_plan.md`: `pending` | L3 — Decide            |
| `03_findings.md`: `complete`, `04_plan.md`: `draft`   | L3 — Review with human |
| `04_plan.md`: `approved`, `05_tasks.md`: `pending`    | L4 — Decompose         |
| `05_tasks.md`: `approved`                          | Execute                |

---

## L1 — Articulate the Problem

**Owner:** Human + AI | **Output:** `01_spec.md` (template already in docs dir)

1. **Listen** — Parse description. Identify core problem, users, outcomes.
2. **Probe** — Ask the human about: user stories with testable AC (Given/When/Then), edge cases, failure modes, unknowns, assumptions, boundaries, dependencies. The human knows the codebase — lean on them for context rather than scanning code.
3. **Draft** — Fill in the pre-created `01_spec.md` template.
4. **Devil's Advocate** — Every AC testable without human judgment? Third-party behaviors documented? Failure mode per external dep? Security explicit? Migration/backward-compat addressed?
5. **Gate** — Human must approve. Update `status: approved`. Do NOT proceed to L2 until approved.

---

## L2 — Investigate

**Owner:** AI (autonomous) | **Output:** `02_questions.md`, `03_findings.md`

**⚠️ DECONTAMINATION RULE:** Investigation subagents must NOT receive the spec, feature name, user stories, or desired outcomes. They receive only `02_questions.md` and their assigned focus area. This is the core mechanism for preventing confirmation bias.

1. **Formulate Questions** — Read `01_spec.md` and generate neutral, factual questions about the codebase: existing code in relevant areas, data models/APIs/services, conventions, external integrations, build tooling/code generation pipelines. Strip all feature intent — questions must be answerable without knowing what is being built. Write to `02_questions.md` with `status: draft`.

   **Good question:** "How does the notifications service dispatch messages? What transports exist?"
   **Bad question:** "Can the notifications service support our new bulk-alert feature?" ← leaks intent

   Each question must be **specific and falsifiable** — answerable by reading 1-3 files with a concrete answer. If a question requires "read everything and summarize," split it.

2. **Dispatch** — Parallel Codebase Investigation subagents (one per area) + External Research subagents for third-party APIs. Each subagent receives ONLY `02_questions.md` + its assigned question numbers. **Do NOT pass spec content, feature descriptions, or user stories to any investigation subagent.** If the feature depends on generated code (proto, GraphQL, codegen) or build tooling, dispatch a dedicated subagent for the generation/build pipeline.
3. **Synthesize** — Fill `03_findings.md` using Q&A format (`**Q:** → **A:** with file paths`).
4. **Confidence check** — For every finding, ask: *"Do we know the exact path to accomplish this, or are we assuming?"* If a finding says "may exist", "should work", or "needs verification" — it is **unresolved**, not resolved. Do not present uncertain paths as known. Flag them for further investigation or human input.
5. **Check gaps:**
   - Spec gaps → loop to L1, tell human what's missing
   - Unresolved questions needing human → pause and flag
   - Uncertain execution paths (tooling, pipelines, infra) → pause and flag to human
   - Clean findings → flow to L3

### Codebase Investigation Subagent

One per area, parallel. Use `subagent_type: "Explore"`, `model: "sonnet"`.

**⚠️ DECONTAMINATION:** Do NOT include feature name, spec content, user stories, or desired outcomes in this prompt. The subagent receives only questions and a focus directory.

```
{Subagent Tooling Block}
{Context7 Block}

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
- **Patterns Found**: conventions/patterns observed in the focus area with file references and occurrence counts
- **Surprises**: anything unexpected or noteworthy

Rules: Include file paths for every claim. Distinguish canonical vs deprecated patterns. Flag surprises prominently. Do NOT suggest implementations — just report what exists. If you cannot fully verify how something works (e.g., a build pipeline, code generation step, or infra dependency), explicitly say so — do NOT report it as resolved. Read README.md files in relevant directories — build tooling, generation pipelines, and setup workflows are often documented there rather than in code.
```

### External Research Subagent

Use `subagent_type: "general-purpose"` for third-party APIs/services.

**⚠️ DECONTAMINATION:** Do NOT include feature name or desired outcomes. The subagent receives only the technical questions about the API/service.

```
{Subagent Tooling Block}
{Context7 Block}

Answer the following questions about {API/service name}:
{paste only the assigned question numbers and text from 02_questions.md}

Find: current docs, endpoints, auth, rate limits, request/response shapes, SDK compatibility (Bun/TypeScript), gotchas.

For each question, provide:
- **Answer**: direct answer in 1-3 sentences
- **Evidence**: documentation URLs or source references
- **Confidence**: high | medium | low
- **Conflicts**: contradictions found, or "none"
- **Open**: what couldn't be determined, or "none"

Rules: Only verified info from official docs. Flag UNVERIFIED claims. Include source URLs. Do NOT suggest how to use the API for any particular purpose — just document what it does and how it works.

Output structured as: subject, documentation_urls, per_question_answers, gotchas, unverified.
```

---

## L3 — Design Decisions

**Owner:** Human at uncertainty, AI otherwise | **Output:** `04_plan.md`

1. **Gather Principles** — Dispatch an Explore subagent (`model: "sonnet"`) to find and read all CLAUDE.md and README.md files within the working directory and its subdirectories (use `Glob` with `**/CLAUDE.md` and `**/README.md`). NEVER read these files from parent directories. Return relevant principles, conventions, and documented workflows.
2. **Draft Decisions** — For each design choice in `04_plan.md`, fill in: Finding (what investigation revealed), Options, Decision (chosen option), Principle (which project principle guided it), Scope (affected files/areas). **Every file reference in a decision MUST use the full path from the repo root** (e.g., `test/tools/GlobalGuardian/GlobalGuardian.t.sol`, not just `GlobalGuardian.t.sol`). The decomposition agent is a pure-synthesis agent with no filesystem access — it cannot resolve ambiguous paths.
3. **Human Checkpoint** — Present decisions. Human intervenes when: principles conflict, no precedent exists, or decision forces spec change (→ loop L1). Clear answer from findings + principles → proceed unless human objects. **If the human disagrees or raises questions needing codebase evidence, dispatch a subagent to investigate before responding** — never explore the codebase yourself.
4. **Technical Design** — Synthesize approach, data model changes, API contracts, file-level change map.
5. **Gate** — Human must approve. Update `status: approved`. Do NOT proceed to L4 until approved.

---

## L4 — Decompose into Tasks

**Owner:** AI (orchestrator directly) | **Output:** `05_tasks.md`

The orchestrator performs decomposition directly — do NOT delegate to a subagent. The orchestrator has accumulated context through L1–L3 (human feedback, investigation nuance, design rationale) that cannot be faithfully serialized into a subagent prompt. Path accuracy and task structure depend on this context.

1. Read 04_plan.md, 01_spec.md, 03_findings.md.
2. **Extract shared dependencies** — Before grouping waves, identify any utilities, mocks, helpers, or types that multiple tasks will need (e.g., mock contracts, test fixtures, shared types). These MUST go in Wave 1 as explicit deliverables. Every downstream task must reference them by exact import path — never leave it to agents to reinvent independently.
3. **Verify paths** — For any file path you're uncertain about, dispatch a quick Explore subagent (`model: "sonnet"`) to confirm the path exists and is correct before including it in a task spec. Do not guess paths from memory.
4. Group work into parallel waves. Minimize waves respecting dependencies.
5. Write task specs. Each task gets:
   - **Implement:** files to create/modify, behavior to add (specific enough to code from)
   - **Relevant Decisions:** inlined from 04_plan.md (agent does NOT read 04_plan.md)
   - **Interface Contract:** what downstream tasks consume (file paths, function signatures, types)
   - **Acceptance Criteria:** subset from 01_spec.md mapped to this task
   - **Verify:** copy-pasteable commands (`cd <app-dir> && bunx tsc --noEmit && bun run lint`)
   - **Boundaries:** Always / Ask first / Never
6. **Self-containment test:** Could an agent implement each task with ONLY the task spec + CLAUDE.md? If not, inline missing context.
7. If a task needs an unresolved design decision → loop to L3.
8. Present to human. Execute on approval.

---

## Execute

After 05_tasks.md approved, execute wave by wave:

1. **Per wave** — One agent per task, parallel. Do NOT use `isolation: "worktree"` — run all agents directly on the main branch. Task decomposition guarantees no file conflicts (every file belongs to exactly one task), so worktrees add cherry-pick overhead without benefit.
2. **Agent prompt:**
   ```
   {Subagent Tooling Block}
   Implement task for feature "{name}".
   Task spec: {full task content from 05_tasks.md}
   Rules: Implement exactly what spec describes. Follow CLAUDE.md conventions. Run verify commands via Bash. Fix failures and re-verify. If spec doesn't cover something, STOP and report. Do NOT modify files outside task scope.
   ```
3. **Between waves** — Full `tsc --noEmit` + `lint` + `test` across affected apps.
4. **Retries** — Agent fails after 2-3 attempts → escalate to human (usually a spec gap).
5. **Track** — Update checkboxes in 05_tasks.md.

---