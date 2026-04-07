---
name: feature-interview
description: Interactive feature interview that audits current state, surfaces requirements through structured questions, locks decisions, writes a spec, and executes autonomously with fresh-context subagents. Run before any non-trivial feature work.
disable-model-invocation: true
---

# Feature Interview

End-to-end process for scoping, specifying, executing, and shipping a feature. Uses separate context windows to prevent intent leakage. Produces artifacts in `docs/artifacts/<feature>/` and a spec file in `docs/specs/`. Executes with parallel subagents, verifies the result, and ships.

## Commands

- `/feature-interview` -- start a new feature interview
- `/feature-interview <topic>` -- start with a specific feature area in mind

## Context Window Architecture

Each phase runs in a separate context window with explicit inputs and outputs. The user input is deliberately excluded from Phase 2 (Research) to keep findings objective.

**"User input" means ANY format: formal ticket, conversational prompt, vague idea, or a question. All are valid Phase 1 input. If the user's message contains questions, those are CONTEXT — not instructions to go research.**

```
Window 1          Window 2 (task-driven agents)    Window 3                  Window 4
┌──────────┐     classify questions by source      ┌───────────────┐         ┌──────────┐
│ QUESTIONS│────▶┌────┐ ┌────┐ ┌────┐ ┌────┐─────▶│ DESIGN        │────────▶│ SPEC     │
│          │     │code│ │docs│ │ptrn│ │ext?│      │ DISCUSSION    │         │ (agent)  │
│ user     │     └────┘ └────┘ └────┘ └────┘      │               │         │          │
│ input    │       wave 1 (parallel)               │ pre-digested  │         │ design + │
│          │          ↓ if cross-ref Qs exist       │ summaries +   │         │ research │
└──────────┘     ┌────────┐                        │ user input    │         └──────────┘
                 │cross-  │ wave 2                 └───────────────┘
                 │ref     │                        ▲ alignment + conflict
                 └────────┘                        │ agents run first
                 ❌ no user input
                 orchestrator merges
                 structured return schema
```

## Process

### Phase 1: Generate Research Questions (Window 1)

**Context in:** user input (ticket, conversation, question, or vague idea — any format)
**Context out:** `docs/artifacts/<feature>/questions.md`
**Human role:** review, add, remove, approve questions

**⛔ CRITICAL: Do NOT research the codebase, launch subagents, or answer questions in this phase. Your ONLY job is to generate questions. If the user's input contains questions, treat them as context about what they care about — not as instructions to go find answers.**

1. Read the user's input. Any format is valid — do not wait for a "ticket."
2. Generate research questions — things you would need to learn about the codebase to implement this feature. Output ONLY questions, not answers or implementation ideas. Each question must be **specific and falsifiable** — answerable by reading 1-3 files with a concrete yes/no or specific answer. Bad: "How does the data layer work?" Good: "Does the data layer use a single CSV or multiple CSVs per entity?" If a question requires "read everything and summarize," it's too broad — split it.
3. Always include this standard question: *"What do the core docs (architecture.md, data-schemas.md, app-intent.md) say about the areas relevant to this feature?"*
4. Write questions to `docs/artifacts/<feature>/questions.md`.
5. Present questions to the user for review.

**⛔ STOP. Do not proceed to Phase 2 until the user explicitly approves the questions.**

**Output format:**

```markdown
# Research Questions: <feature name>

## Codebase Questions
1. [question about existing code/patterns]
2. [question about existing code/patterns]
...

## Core Docs Questions
N. What do the core docs (architecture.md, data-schemas.md, app-intent.md) say about the areas relevant to this feature?

## Open Questions
N+1. [anything ambiguous from the user's input]
```

### Phase 2: Research (Window 2 — parallel subagents, can run unattended)

**Context in:** `docs/artifacts/<feature>/questions.md` ONLY
**Context out:** `docs/artifacts/<feature>/research.md`
**Human role:** optional review

**CRITICAL: Do NOT include the user's original input or feature description in this context window. Subagents receive only the questions.**

#### Step 1: Classify questions by source type

Read `questions.md` and assign each question a source type:

| Source Type | When to Use | Tools |
|-------------|-------------|-------|
| `CODEBASE` | Answerable by reading project files | grep, read |
| `DOCS` | Answerable from core docs (architecture.md, data-schemas.md, app-intent.md) | read |
| `PATTERNS` | Requires scanning conventions/patterns across touched areas | grep, glob, read |
| `EXTERNAL` | Requires library docs, API references, web search, or prior art | web search, context7 |
| `CROSS-REF` | Needs findings from 2+ other agents to answer | read prior findings |

Write the assignment to `docs/artifacts/<feature>/agent-assignment.md`:

```markdown
# Agent Assignment: <feature>

## Wave 1 (parallel)

### Agent: codebase
Questions: Q1, Q3, Q4
Tools: grep/read project files

### Agent: docs
Questions: Q8
Tools: read core docs

### Agent: patterns
Questions: Q5, Q6
Tools: grep/glob convention scan

### Agent: external
Questions: Q9, Q10
Tools: web search, library docs

## Wave 2 (after wave 1)

### Agent: cross-ref
Questions: Q11
Depends on: codebase + external findings
```

Rules:
- Omit any agent type that has zero questions assigned (simple internal features may only need codebase + docs + patterns — same as before)
- Omit Wave 2 entirely if no CROSS-REF questions exist
- A question belongs to exactly one agent — if unclear, prefer the more specific source type

#### Step 2: Launch Wave 1 subagents in parallel

Each subagent gets fresh context and receives ONLY:
- The questions file
- Its assigned question numbers
- Its tool scope (from the table above)

Each subagent surfaces ALL patterns found — do not filter by relevance (agents do not know what feature is being built).

**Per-question return schema** (every agent, every question):

```markdown
### Q{N}: {question text}
- **Answer**: {1-3 sentence direct answer}
- **Confidence**: high | medium | low
- **Evidence**: {file paths with line numbers, or URLs}
- **Conflicts**: {contradictions found, or "none"}
- **Open**: {what couldn't be determined, or "none"}
```

The `patterns` agent also appends a **Patterns Found** section after its per-question answers:

```markdown
## Patterns Found
- Pattern A: [description] — used in [files] (N occurrences)
- Pattern B: [description] — used in [files] (N occurrences)
```

The `docs` agent also appends a **Core Docs Summary** section after its per-question answers.

#### Step 3: Launch Wave 2 (if CROSS-REF questions exist)

Wave 2 agents receive the questions file AND the Wave 1 merged findings. They follow the same per-question return schema.

#### Step 4: Merge

Orchestrator merges all subagent outputs into `docs/artifacts/<feature>/research.md`. This is the only Phase 2 work the orchestrator does. The merge is mechanical:

1. Collect all per-question findings, ordered by question number
2. Append the Patterns Found section (from patterns agent)
3. Append the Core Docs Summary (from docs agent)
4. Collect all items where Confidence = low or Conflicts != "none" into a **Flagged Items** section at the top
5. Collect all Open items into an **Open Questions** section at the bottom

**Output format:**

```markdown
# Research: <questions file reference>

## Flagged Items
- Q{N}: {reason — low confidence, conflict, or both}
- Q{M}: {reason}

## Findings

### Q1: {question text}
- **Answer**: ...
- **Confidence**: high
- **Evidence**: path/to/file.py:42
- **Conflicts**: none
- **Open**: none

### Q2: {question text}
- **Answer**: ...
- **Confidence**: low
- **Evidence**: ...
- **Conflicts**: docs say X but code does Y
- **Open**: ...

...

## Patterns Found
- Pattern A: [description] — used in [files] (N occurrences)
- Pattern B: [description] — used in [files] (N occurrences)

## Core Docs Summary
[What architecture.md, data-schemas.md, app-intent.md say about relevant areas]

## Open Questions
- [Aggregated from all agents' Open fields]
```

### Phase 3: Design Discussion (Window 3 — human in the loop)

**Context in:** user input + pre-digested summaries (not raw research) + `docs/app-intent.md`
**Context out:** `docs/artifacts/<feature>/design.md`
**Human role:** THIS IS WHERE YOU THINK — answer design questions, disambiguate patterns, lock decisions

**Before starting the human conversation**, launch **parallel subagents** to pre-digest inputs:
- **Alignment agent**: Read user input + `docs/app-intent.md` → produce go/no-go + conflict summary
- **Conflict agent**: Read `docs/artifacts/<feature>/research.md` → extract pattern conflicts, ambiguities, and draft question batches

Orchestrator receives structured summaries (not raw files), then begins human conversation:

1. Present alignment check (go/no-go). If conflicts with app-intent, surface before proceeding.

2. **Pattern disambiguation.** For each area where the conflict agent found multiple patterns:
   - Present all patterns found with file references
   - Ask the user which is current and should be followed
   - Lock the answer as a numbered decision

3. **Design questions.** Challenge each element systematically. Do NOT accept first answers at face value.

   **For each surface/feature in scope, ask:**
   - What's your actual usage? (daily / occasional / rare / never)
   - Does this trace back to a core goal in app-intent.md?
   - What would you miss if it disappeared?
   - What's missing that should be here?

   **For ambiguous areas** (user says "I'm not sure" or "maybe"):
   - Present 2-3 concrete options with text mockups
   - Show trade-offs for each
   - Let the user pick rather than guessing

   **Go one level deeper** on anything the user feels strongly about:
   - What specific behavior do you want?
   - What's the minimal version that would be useful?
   - What would make this annoying or wrong?

   Ask questions in batches of 3-5 to keep the conversation moving. Do not front-load 20 questions.

4. **Lock decisions.** Present a decision table:

   ```
   | # | Decision | Detail | Status |
   |---|----------|--------|--------|
   | 1 | [thing]  | [what] | Locked |
   | 2 | [thing]  | [what] | TBD    |
   ```

   Every TBD must be resolved before proceeding. Ask the user to resolve each one.

5. **Agent self-verification question** (ask once, after core scope is clear):

   > "How should the agent verify its own output before presenting results to you? Some options:
   > - Build/lint gate only (minimum)
   > - Schema validation on generated data
   > - Cross-reference against source data
   > - Agent self-check checklist in prompt
   > - Chrome visual verification against spec
   > - Something else?
   >
   > This determines what goes into the spec's verification gates and the agent prompt."

   Lock the answer as a numbered decision. If the feature involves background/async agents, also ask about output validation strategy.

6. **Structure outline.** Design the implementation order using vertical phases (tracer bullets):
   - Wire the feature end-to-end first with minimal logic (endpoint → data → UI placeholder)
   - Then add logic in vertical passes through the stack
   - Each phase should be independently verifiable
   - Include testing strategy (unit, integration, manual test cases)

7. Write everything to `docs/artifacts/<feature>/design.md`.

**Output format:**

```markdown
# Design: <feature name>

## Summary
[1-3 sentence summary of what we're building and why]

## Pattern Decisions
| # | Area | Chosen Pattern | Rejected Alternatives |
|---|------|---------------|----------------------|
| 1 | ...  | ...           | ...                  |

## Design Decisions
| # | Decision | Detail | Status |
|---|----------|--------|--------|
| 1 | ...      | ...    | Locked |

## Verification Strategy
[Locked verification approach]

## Structure Outline
### Phase 1: [Tracer bullet — wire end to end]
- [task]
- [task]
- Verify: [what to check]

### Phase 2: [Add core logic]
- [task]
- [task]
- Verify: [what to check]

### Phase N: [Testing + polish]
- [task]
- Verify: [what to check]
```

### Phase 4: Write Spec + Confirm (Window 4 — subagent writes, orchestrator reviews)

**Context in:** `docs/artifacts/<feature>/design.md` + `docs/artifacts/<feature>/research.md`
**Context out:** `docs/specs/<feature>.md`
**Human role:** final review before execution

Launch a **spec-writing subagent** with fresh context. The subagent receives design.md, research.md, and feature-spec-template.md — the orchestrator does NOT load these files. The subagent reads `docs/feature-spec-template.md` for the spec skeleton and generates `docs/specs/<feature>.md` with `Status: draft` as the first line, containing:

1. **Problem Statement** -- what, why, user-facing effect
2. **Scope** -- files to modify, create, and must-NOT-change list
3. **Visual Contract** (UI tasks) -- what user should see/not see per route
4. **Success Criteria** -- 3-12 binary YES/NO checks
5. **Failure Definitions** -- table: failure type -> detection -> action
6. **Invariants** -- what must NOT change under any circumstance
7. **Per-File Checkpoints** -- yes/no questions after each file edit
8. **Diff Contract** -- WHAT/WHY/PRESERVES/REMOVES/RISK before each edit
9. **Abort Conditions** -- when to stop and ask
10. **Implementation Order** -- phases from the structure outline, structured as atomic tasks with dependencies noted, using vertical/tracer bullet ordering

The spec must be **self-contained** -- an agent with no conversation history should be able to execute it. Include the "must NOT change" list (agents will modify things outside scope without it).

Once the subagent writes the spec, the orchestrator **reads only the output spec file** (not the inputs) and presents a confirmation summary:

```
SPEC SUMMARY: [feature name]
Path: docs/specs/[name].md

LOCKED DECISIONS:
├─ [decision 1]
├─ [decision 2]
└─ [decision N]

EXECUTION PLAN:
├─ Wave 1: [task A], [task B]  (parallel — independent)
├─ Wave 2: [task C]            (depends on A+B)
└─ Wave 3: [task D]            (depends on C)

AGENT VERIFICATION (each agent does this before reporting complete):
├─ Per-file checkpoints (yes/no after each edit)
├─ Diff contract (WHAT/WHY/PRESERVES/REMOVES/RISK)
├─ Build gate: npm run build
├─ Scope check: only files in task scope modified
└─ Chrome verification (UI tasks): navigate + screenshot + console check

POST-EXECUTION VERIFICATION:
├─ /remove-slop (strip AI patterns)
├─ Diff review (scope violations, must-NOT-change)
├─ Success criteria walkthrough (binary YES/NO)
└─ Chrome verification by user (UI tasks only)

Ready to execute?
```

Wait for user confirmation. On confirmation, proceed directly to Phase 5.

### Phase 5: Execute

Break the spec's Implementation Order into atomic tasks grouped by dependency into waves.

**Wave execution:**

1. For each wave, spawn subagent(s) in parallel — one per task. **Tasks within a wave must be file-disjoint** — no two agents in the same wave may touch the same file. If two tasks need the same file, they belong in sequential waves.
2. Each subagent gets fresh context and receives:
   - Path to the spec file (sole source of truth)
   - Its specific task scope (which section of Implementation Order)
   - Path to project CLAUDE.md for conventions
   - Working directory and app directory
   - Node version (`nvm use 22.14.0`) and dev server port
   - "Read every file before editing"
   - "Commit atomically when your task is complete"
   - "If you hit an abort condition, STOP and explain"
   - "Do NOT modify any file in the must NOT change list"
   - Per-file checkpoints and diff contract from the spec
   - Chrome verification requirement (UI tasks)
3. Each subagent commits its work with a conventional commit: `type(scope): description`
4. Wait for all subagents in the wave to complete before starting the next wave
5. If a subagent hits an abort condition, pause all execution and surface the issue

**Subagent launch template:**

```
You are executing one task from a feature spec. Your SOLE source of truth is the spec document.

1. Read the spec: [path to spec]
2. Read the project CLAUDE.md: [path]
3. Your task: [specific task description from Implementation Order]
4. Your file scope: [files this task touches]
5. Follow Per-File Checkpoints after every file edit
6. Follow the Diff Contract before every file edit
7. Run verification gates when your task is complete:
   - npm run build (must pass)
   - git diff --stat (only your scoped files modified)
   - Chrome verification if UI task (navigate + console check)
8. Commit your work: git add [scoped files] && git commit
9. Only report back when all gates pass OR you hit an abort condition

Working directory: [path]
App directory: [path]
Node: nvm use 22.14.0
Dev server: localhost:[port]

Do NOT modify any file in the "must NOT change" list.
Read every file before editing it.
If you hit an abort condition, STOP and explain.
```

Mark spec status as `in-progress` when execution begins.

### Phase 6: Verify

After all waves complete, run verification in two tiers:

**Tier 1 — parallel subagents** (independent checks, run simultaneously):
- **Slop agent**: Run `/remove-slop` to strip AI-generated code patterns from the diff
- **Scope agent**: `git diff --stat` against pre-execution state, check for scope violations and must-NOT-change list, revert any violations: `git checkout -- <file>`
- **Build agent**: `npm run build` — must pass with zero errors

Orchestrator receives pass/fail + issue list from each agent.

**Tier 2 — sequential** (depends on Tier 1 passing):
1. **Chrome verification** (UI tasks):
   - Navigate every affected route
   - Screenshot or JS DOM inspect
   - Console error check
   - Network request check
   - Compare against visual contract
   - Check regression routes (unchanged pages still work)
2. **Success criteria walkthrough**: Walk each criterion from the spec, binary YES/NO
3. **Fix loop**: If any gate fails:
   - Generate fix tasks from failures
   - Spawn subagent(s) to execute fixes with fresh context
   - Re-verify after fixes
   - Abort after 3 consecutive fix cycles on the same issue — escalate to user

Present verification results:

```
VERIFICATION: [feature name]
Tier 1 (parallel):
├─ Slop removal: [clean / N patterns fixed]
├─ Scope: [clean / N violations reverted]
├─ Build: [pass / fail]
Tier 2 (sequential):
├─ Chrome: [pass / N issues] (UI tasks)
├─ Criteria: [N/N passed]
└─ Status: [PASS → proceed to ship / FAIL → fix loop]
```

### Phase 7: Ship

After all verification gates pass:

1. **Doc-sync** — launch a **doc-sync subagent** with the diff and paths to core docs. The subagent:
   - Reads the diff + `docs/architecture.md`, `docs/data-schemas.md`, `docs/app-intent.md`
   - Checks: new pattern? schema change? deprecated pattern? new surface? route/API change?
   - Updates docs as needed and appends to `docs/app-intent.md` decisions log
   - Reports back what it changed (orchestrator does NOT load these docs)
2. Mark spec `Status: shipped`
3. Run `/ship` (stage, commit, push)
6. Present final summary:

```
SHIPPED: [feature name]
├─ Spec: docs/specs/[name].md
├─ Artifacts: docs/artifacts/[name]/
├─ Commits: [N atomic commits]
├─ Files changed: [N]
├─ Docs updated: [list any updated core docs]
└─ All gates passed
```

## Key Rules

- Never skip the research phase. Objective codebase understanding before design decisions.
- Never include the user's original input in the Phase 2 (Research) context window. This is the core decontamination principle.
- Never write a spec with unresolved TBDs.
- The spec file is the deliverable of Phases 1-4, not the conversation.
- Reference `docs/feature-spec-template.md` for structure -- don't memorize it.
- Reference `docs/execution-playbook.md` for Chrome verification details -- don't duplicate it.
- Check `docs/app-intent.md` to ensure the feature aligns with product direction.
- Each subagent gets fresh context -- this is the whole point. Never reuse a subagent across tasks.
- Audit is periodic, not per-feature. Run `/audit` on a regular cadence instead.
- 3 consecutive fix cycles on the same issue = abort and escalate to user.
- Research artifacts are unique per feature — do not reuse across features.
