---
name: feature-interview
description: Use when decomposing an ADO feature into user stories. Interactive TA workflow that researches the codebase, surfaces requirements through structured questions, locks decisions, drafts acceptance criteria, and creates ADO user stories. Also supports retrospectives on completed features.
---

# Feature Interview — Technical Analysis Workflow

TA workflow for decomposing an ADO feature into well-scoped user stories with acceptance criteria. Researches the codebase, surfaces requirements through structured discussion, and creates stories in Azure DevOps. Runs a retrospective after development to capture learnings.

## Commands

```
/feature-interview                    — start new TA
/feature-interview <ticket-url>       — start TA with specific ticket
/feature-interview retro <feature>    — run retrospective on completed feature
```

Parse the first argument: if `retro`, jump to Phase 5. Otherwise, run the normal TA flow starting at Phase 1.

## Project Config

```yaml
# ── PROJECT CONFIG ──────────────────────────────────────────
projects:
  - name: "MyApp.Web"               # display name
    path: "src/web"                  # relative to repo root
    stack: "React 18 + TypeScript"   # for context in research
    claude_md: "src/web/CLAUDE.md"   # project-level instructions (optional)

  - name: "MyApp.API"
    path: "src/api"
    stack: ".NET 8 + ASP.NET Core"
    claude_md: "src/api/CLAUDE.md"

# ADO config
ado_org: "https://dev.azure.com/devonenergy"
ado_project: "DVN"

# Core docs the skill checks during research (create over time, not required)
core_docs:
  - "docs/app-intent.md"
  - "docs/architecture.md"
  - "docs/data-schemas.md"
  - "docs/features.md"
# ────────────────────────────────────────────────────────────
```

**Minimum viable config:** One project with `name`, `path`, `stack`. ADO config defaults to Devon Energy org/project.

## Artifact Structure

**Everything lives in `~/.claude/projects/DSC/` — nothing written to the repo.**

```
~/.claude/projects/DSC/
  ta-knowledge-base.md                    # Global learnings, persists forever

  artifacts/<feature>/
    questions.md                          # Phase 1 → consumed by Phase 2
    research.md                           # Phase 2 → consumed by Phase 3
    analysis.md                           # Phase 3 → consumed by Phase 4 + Phase 5

  retros/<feature>/
    retrospective.md                      # Phase 5 → persists as historical record
```

**Lifecycle:**
- `questions.md`, `research.md`: Ephemeral. Deleted at end of Phase 4 after stories are created.
- `analysis.md`: Kept until retro runs (Phase 5 needs it). Deleted after retro.
- `retrospective.md`: Persists as a historical record.
- `ta-knowledge-base.md`: Persists forever. Accumulates learnings from all retros.

## ADO Attachment Handling

When the ticket or its comments contain attachments (screenshots, documents):

1. **ALWAYS use a subagent** to download attachments. NEVER download directly in the main thread — this can crash the session.
2. The subagent should:
   a. Get an Azure DevOps access token:
      `az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798`
   b. Download with curl using Bearer auth to `/tmp/<filename>`
   c. Report success/failure and file path
3. After the subagent confirms success, read the file in the main thread (e.g., Read tool for images/PDFs).

## Knowledge Base

**Location:** `~/.claude/projects/DSC/ta-knowledge-base.md`

**Structure:**

```markdown
# TA Knowledge Base

## Domain Knowledge
Corrections and context about how the app actually works.
- [date] [context]: [what is actually true about the app]

## TA Process Learnings
What worked and didn't work in past TAs. Fed by retrospectives.
- [date] [feature]: [learning]

## Recurring Edge Cases
Edge case patterns that recur across features.
- [pattern]: [what to check for]
```

**How it's used:**
- **Phase 1** reads it to avoid asking questions already answered by domain knowledge
- **Phase 3** reads it to apply process learnings and check for recurring edge case patterns
- **Phase 5 (Retro)** writes to it — distills retrospective findings into global learnings
- **Any phase** where the user corrects an assumption: write the correction to Domain Knowledge immediately

**Immediate correction rule:** When the user says "that's not how it works" or corrects an assumption about the app, write the correction to the Domain Knowledge section of the knowledge base right then — do not defer to retrospective.

---

## Phase 1: Generate Research Questions

**Context in:** ticket/feature description + knowledge base + ADO parent feature data
**Context out:** `~/.claude/projects/DSC/artifacts/<feature>/questions.md`
**Human role:** review, add, remove, approve questions

### Pre-steps

1. **Read the knowledge base.** Load `~/.claude/projects/DSC/ta-knowledge-base.md` if it exists. Apply domain knowledge to avoid re-asking answered questions.

2. **Query ADO parent feature.** Fetch the parent feature's work item data and child relations to understand what stories already exist. This prevents duplicate story creation.
   ```
   az boards work-item show --id <feature-id> --organization https://dev.azure.com/devonenergy --expand relations -o json
   ```

3. **Fetch all comments.** The `System.History` field only returns the latest comment. To get ALL comments on a work item, use the REST API.

   **IMPORTANT:** `az rest` returns raw JSON from the API — do NOT add `-o json` (that flag tells the CLI to reformat and can crash on nested responses). Pipe directly or save to a temp file.

   ```bash
   # Save to temp file first, then parse — avoids crash if API returns an error
   az rest --method GET \
     --url "https://dev.azure.com/devonenergy/DVN/_apis/wit/workItems/<feature-id>/comments?api-version=7.1-preview.4" \
     --output-file /tmp/feature-<feature-id>-comments.json 2>/dev/null

   # Check if the file exists and is valid JSON before parsing
   python3 -c "import json; data=json.load(open('/tmp/feature-<feature-id>-comments.json')); [print(c.get('text','')) for c in data.get('comments',[])]"
   ```

   Do NOT use `az devops invoke` for this — it fails with JSON parsing errors. Do NOT rely on `System.History` — it only has the most recent comment. Comments often contain critical context, stakeholder decisions, and attachment references.

   **If the comment fetch fails** (auth error, 404, empty response), log it and continue — the work item fields from step 2 are sufficient to proceed. Comments are supplementary context, not a blocker.

4. **Check for attachments (MANDATORY subagent).** If the ticket or its comments reference attachments (images, docs), you MUST use the Agent tool to spawn a subagent for each download. NEVER download attachments in the main thread — this crashes the session. Follow the ADO Attachment Handling instructions above exactly. Read downloaded files in the main thread only after the subagent confirms success.

5. **Ask for supplemental context.** Before generating questions, ask:

   > "Is there any context not captured in the ADO ticket? Examples: Teams messages, meeting notes, screenshots, mockups, verbal decisions, stakeholder constraints. You can paste text or drop images here."

   Wait for the user's response. If they provide additional context, incorporate it alongside the ticket when generating questions. If they say none, proceed.

### Question generation

1. Read the ticket or feature description provided by the user (plus any supplemental context from pre-step 4).
2. Identify which project(s) are in scope based on the project config.
3. Generate research questions — things you need to learn about the codebase to **decompose this feature into well-scoped stories**. Output ONLY questions, not answers or implementation ideas.
4. Always include: *"What do the core docs say about the areas relevant to this feature?"* (Check each path in `core_docs` config.)
5. Always include a question about deployment/rollout constraints (feature flags, phased rollout, migration needs).
6. Write questions to `~/.claude/projects/DSC/artifacts/<feature>/questions.md`.
7. Present questions to the user for review. Wait for approval before proceeding.

**Output format:**

```markdown
# Research Questions: <feature name>

## Scope: [which project(s) from config]

## Existing Stories
[List any child stories already linked to the parent feature, or "None"]

## Codebase Questions
1. [question about existing code/patterns]
2. [question about existing code/patterns]
...

## Core Docs Questions
N. What do the core docs say about the areas relevant to this feature?

## Deployment/Rollout Questions
N+1. [constraints, feature flags, migration needs]

## Open Questions
N+2. [anything ambiguous from the ticket itself]
```

---

## Phase 2: Research (can run unattended)

**Context in:** `~/.claude/projects/DSC/artifacts/<feature>/questions.md` ONLY
**Context out:** `~/.claude/projects/DSC/artifacts/<feature>/research.md`
**Human role:** optional review

**CRITICAL: Do NOT include the ticket or feature description in this context window. The subagent receives only the questions.**

1. Launch a subagent with fresh context. Pass it ONLY the questions file.
2. The subagent reads the codebase to answer each question.
   - Explore each project's `path` from the config
   - Read each project's `claude_md` if it exists
   - **Exclude test automation code** (Selenium tests, e2e test files, `*.spec.ts`, `*.test.ts`, `*.java` test files) from findings that will feed into Technical Notes. Test automation references in story descriptions confuse developers. If test files are relevant to answering a research question, note them in a separate "Test Files Found" subsection — not mixed into the main findings.
3. Surface ALL production code patterns found — do not filter by relevance (the subagent does not know what feature is being analyzed).
4. **Trace shared dependencies.** For each module/service/query/model touched by the research questions, identify other modules that share the same dependency. This feeds the Impact Area analysis in Phase 3.
5. Note any open questions that could not be answered from the codebase.
6. Write findings to `~/.claude/projects/DSC/artifacts/<feature>/research.md`.

**Output format:**

```markdown
# Research: <questions file reference>

## Findings

### [Question 1 text]
[Objective findings with file paths and line numbers]

### [Question 2 text]
[Objective findings]

...

## Patterns Found
- Pattern A: [description] -- used in [files] (N occurrences)
- Pattern B: [description] -- used in [files] (N occurrences)

## Boundaries Found
[API/module/database boundaries discovered — these inform story decomposition]
- Boundary: [description] -- [which modules/services it separates]

## Risk Indicators
[Missing tests, tight coupling, conflicting patterns — these inform story sizing]
- Risk: [description] -- [impact on decomposition]

## Shared Dependencies
[For each service/query/model/API endpoint touched by the research, list other modules that consume it]
- [Service/Query/Model]: consumed by [Module A], [Module B] -- [read-only / shared mutation / DB-level]

## Core Docs Summary
[What core docs say, OR "Core docs not yet created -- here's what was observed"]

## Open Questions
- [Things that could not be determined from the codebase]
```

---

## Phase 3: Analysis Discussion (human in the loop)

**Context in:** ticket + `~/.claude/projects/DSC/artifacts/<feature>/research.md` + core docs (if they exist) + knowledge base
**Context out:** `~/.claude/projects/DSC/artifacts/<feature>/analysis.md`
**Human role:** THIS IS WHERE YOU THINK — answer design questions, disambiguate patterns, decompose features, lock decisions

**Context budget:** If the discussion exceeds ~30 exchanges, write an interim `~/.claude/projects/DSC/artifacts/<feature>/analysis-draft.md` capturing all locked decisions so far, then continue in a fresh window that loads only the draft + remaining TBDs.

### Steps

1. **Load learnings.** Read `~/.claude/projects/DSC/ta-knowledge-base.md`. Apply relevant context corrections, domain knowledge, and past process feedback. Call out any learnings that directly affect this feature.

2. **Read inputs.** Read the ticket, research doc, and core docs (if they exist). Check that the feature aligns with product direction.

3. **Design questions.** Challenge each element systematically. Do NOT accept first answers at face value.

   **For each surface/feature in scope, ask:**
   - What's the actual user workflow? (step by step)
   - What exists today vs. what's new?
   - What are the data dependencies?
   - What should NOT change?

   **For ambiguous areas** (user says "I'm not sure" or "maybe"):
   - Present 2-3 concrete options with trade-offs
   - Let the user pick rather than guessing

   **Go one level deeper** on anything the user feels strongly about:
   - What specific behavior do you want?
   - What's the minimal version that would be useful?
   - What would make this annoying or wrong?

   Ask questions in batches of 3-5 to keep the conversation moving.

4. **Apply decision frameworks.** Before locking decisions, apply the right mental model. Pick the one that fits, don't present as a menu:

   - Feature scope too broad? → **Pareto**: find the 20% that delivers 80%
   - Challenging "we always do it this way"? → **First principles**: rebuild from base truths
   - Need to surface risks? → **Inversion**: what guarantees failure?
   - Choice has downstream effects? → **Second-order thinking**: then what?
   - Multiple approaches, unclear winner? → **Opportunity cost**: what do you give up?
   - Feature feels heavy? → **Via negativa**: what to remove?
   - Need to prioritize across stories? → **Eisenhower matrix**: urgent vs important
   - Short-term vs long-term tension? → **10/10/10**: 10 minutes, 10 months, 10 years

   Apply 1-2 per discussion, not all of them.

5. **Lock decisions.** Present a decision table:

   ```
   | # | Decision | Detail | Status |
   |---|----------|--------|--------|
   | 1 | [thing]  | [what] | Locked |
   | 2 | [thing]  | [what] | TBD    |
   ```

   Every TBD must be resolved before proceeding.

6. **Feature decomposition.** Break the feature into stories by system boundary, user workflow, or data entity. Each story must be independently testable. Use the Boundaries Found and Risk Indicators from research to inform decomposition.

7. **Edge case surfacing.** Systematic per-story edge case analysis. Check for recurring edge case patterns from the knowledge base. Each edge case must be assigned to a specific story — no orphaned edge cases.

8. **Acceptance criteria drafting.** Given/When/Then format, binary testable. Each story gets its own criteria.

9. **Impact area analysis.** For each story, trace the modified files/services/queries/models through the codebase using the shared dependency data from Phase 2 research. For each story, answer:
   - **What modules are affected** beyond the story's direct scope?
   - **Why** — which shared code/service/model/API endpoint creates the dependency?
   - **What to test** — specific regression checks for the tester.

   Assign each impact item a risk level:
   | Risk | Trigger |
   |------|---------|
   | **Low** | Read-only dependency (consumes but doesn't mutate shared data) |
   | **Medium** | Shared service or query (changes could alter behavior for other consumers) |
   | **High** | Database-level change, shared model mutation, or API contract change |

10. **Tester notes.** For each story, write testing guidance: what to verify manually, suggested test case outlines, any special data setup or preconditions needed. This feeds the QA team's test case generation — it is NOT the acceptance criteria (those are binary pass/fail), it's the "how to test" companion.

11. **Story ordering.** Dependency graph: which stories can be parallel, which are sequential. Note any stories that are blocked by external dependencies.

10. Write everything to `~/.claude/projects/DSC/artifacts/<feature>/analysis.md`.

**Output format:**

```markdown
# Analysis: <feature name>

## Summary
[1-3 sentence summary of what we're decomposing and why]

## Scope
[which project(s)]

## Design Decisions
| # | Decision | Detail | Status |
|---|----------|--------|--------|
| 1 | ...      | ...    | Locked |

## Stories

### Story 1: [title]
**Scope:** [which project(s), which modules]
**Summary:** [what this story delivers]
**Acceptance Criteria:**
- Given [context], When [action], Then [result]
- Given [context], When [action], Then [result]
**Edge Cases:**
- [edge case and expected behavior]
**Technical Notes:** [production code patterns, risks — NO test automation code]
**Tester Notes:** [testing guidance: what to verify, suggested test cases, data setup needs]
**Impact Area:**
| Module | Why (shared dependency) | What to Regression Test | Risk |
|--------|------------------------|------------------------|------|
| [module] | [shared service/query/model/API] | [specific checks] | Low/Med/High |
**Dependencies:** [other stories or external]
**Sizing Notes:** [risk indicators, complexity signals]

### Story 2: [title]
...

## Story Dependency Graph
```
[Story 1] ──→ [Story 3]
[Story 2] ──→ [Story 3]
[Story 4] (independent)
```

## Deferred / Out of Scope
- [anything explicitly excluded and why]
```

---

## Phase 4: Story Draft + ADO Creation

**Context in:** `~/.claude/projects/DSC/artifacts/<feature>/analysis.md`
**Context out:** ADO user stories linked to parent feature
**Human role:** review story plan, approve before creation

### Sub-phase 4a: Draft Review

Present a summary of all stories to be created:

```
STORY PLAN: [feature name]
Parent: [ADO feature ID]

STORIES:
+-- Story 1: [title] — [1-line scope]
+-- Story 2: [title] — [1-line scope]
+-- Story N: [title] — [1-line scope]

DEPENDENCY ORDER:
+-- Parallel: [Story 1, Story 2]
+-- Sequential: [Story 3] (after 1+2)

DEFERRED:
+-- [anything out of scope, to be noted on parent]

Ready to create in ADO?
```

Wait for user confirmation before proceeding.

### Sub-phase 4b: ADO Creation

**Create stories in dependency order.** Use the story dependency graph from Phase 3 to determine creation sequence — prerequisite stories are created first. This ensures predecessor/successor links point the right direction.

For each story (in dependency order):

1. **Create User Story** with two separate fields:

   **Description** (`--description`) — HTML containing these sections (in order):
   - **Summary** — what this story delivers
   - **Scope** — modules/files involved
   - **Edge Cases** — per-story edge cases with expected behavior
   - **Technical Notes** — production code patterns, risks from research. **Exclude all test automation code** (Selenium, e2e, spec/test files). Devs don't need test file references here.
   - **Tester Notes** — testing guidance for QA: what to verify, suggested test case outlines, data setup needs. This feeds test case generation.
   - **Impact Area** — HTML table with columns: Module | Why (shared dependency) | What to Regression Test | Risk (Low/Med/High). Based on shared dependency tracing from Phase 2/3.
   - Link to analysis artifact: `Analysis: ~/.claude/projects/DSC/artifacts/<feature>/analysis.md`

   **Acceptance Criteria** (`--fields "Microsoft.VSTS.Common.AcceptanceCriteria=<html>"`) — Given/When/Then format, in ADO's dedicated Acceptance Criteria field. **Do NOT put acceptance criteria in the description.**

   ```bash
   az boards work-item create \
     --type "User Story" \
     --title "[story title]" \
     --description "<html description>" \
     --fields "Microsoft.VSTS.Common.AcceptanceCriteria=<html acceptance criteria>" \
     --area "[area path from parent feature]" \
     --project DVN \
     --organization https://dev.azure.com/devonenergy \
     -o json --query "id"
   ```

2. **Link as child** of parent feature:
   ```bash
   az boards work-item relation add \
     --id [story-id] \
     --relation-type parent \
     --target-id [parent-feature-id] \
     --organization https://dev.azure.com/devonenergy \
     -o none
   ```

3. **Link predecessor/successor** for sequential dependencies from the dependency graph. The predecessor (must-happen-first) story gets the `Predecessor` relation pointing to the successor (happens-after) story:
   ```bash
   az boards work-item relation add \
     --id [predecessor-story-id] \
     --relation-type "System.LinkTypes.Dependency-Forward" \
     --target-id [successor-story-id] \
     --organization https://dev.azure.com/devonenergy \
     -o none
   ```
   Skip this step for stories that are independent/parallel.

4. **Leave unassigned, unsprinted** unless told otherwise.

5. After all stories are created, **add summary comment to parent feature**:
   ```bash
   az boards work-item update \
     --id [parent-feature-id] \
     --discussion "<b>TA Complete</b><br>Created [N] stories from technical analysis.<br><ul><li>[story titles with IDs]</li></ul>" \
     --organization https://dev.azure.com/devonenergy \
     -o none
   ```

### Post-creation cleanup

- Delete `~/.claude/projects/DSC/artifacts/<feature>/questions.md`
- Delete `~/.claude/projects/DSC/artifacts/<feature>/research.md`
- Keep `analysis.md` (needed for retrospective)

Present final summary:

```
TA COMPLETE: [feature name]
Parent: [ADO feature ID]

STORIES CREATED:
+-- #[id]: [title]
+-- #[id]: [title]
+-- #[id]: [title]

ANALYSIS: ~/.claude/projects/DSC/artifacts/<feature>/analysis.md

Run `/feature-interview retro <feature>` after development to capture learnings and clean up.
```

---

## Phase 5: Retrospective (separate invocation)

**Triggered by:** `/feature-interview retro <feature-name>`
**Context in:** `~/.claude/projects/DSC/artifacts/<feature>/analysis.md` + knowledge base + ADO story data
**Context out:** `~/.claude/projects/DSC/retros/<feature>/retrospective.md` + updated knowledge base

1. **Load analysis artifact.** Read `~/.claude/projects/DSC/artifacts/<feature>/analysis.md`. If it doesn't exist, inform user and abort.

2. **Load knowledge base.** Read `~/.claude/projects/DSC/ta-knowledge-base.md`.

3. **Query ADO.** For each story created during the TA:
   - Was it completed, cancelled, or re-scoped?
   - Were acceptance criteria changed during development?
   - Were new stories added that weren't in the original plan?
   - Were stories split or merged?

4. **Structured feedback questions.** Ask the user:
   - Which stories were well-scoped? Which were too big or too small?
   - Were any edge cases missed that should have been caught?
   - Did the acceptance criteria hold up during development?
   - What would you do differently next time?
   - Any domain knowledge corrections? (Things that turned out to work differently than assumed)

5. **Write retrospective** to `~/.claude/projects/DSC/retros/<feature>/retrospective.md`:

   ```markdown
   # Retrospective: <feature name>
   Date: [date]
   Parent Feature: [ADO ID]

   ## Stories Planned vs Actual
   | Story | Planned | Actual | Delta |
   |-------|---------|--------|-------|
   | ...   | ...     | ...    | ...   |

   ## What Worked
   - ...

   ## What Didn't Work
   - ...

   ## Domain Corrections
   - ...

   ## Process Improvements
   - ...
   ```

6. **Update knowledge base.** Distill retrospective findings into `~/.claude/projects/DSC/ta-knowledge-base.md`:
   - Domain corrections → **Domain Knowledge** section
   - Process learnings → **TA Process Learnings** section
   - Recurring edge case patterns → **Recurring Edge Cases** section

7. **Clean up.** Delete `~/.claude/projects/DSC/artifacts/<feature>/` directory (analysis.md and any remaining files).

---

## Key Rules

- Never skip the research phase. Objective codebase understanding before design decisions.
- Never include the ticket in the Phase 2 (Research) context window. This is the core decontamination principle.
- Never proceed to Phase 4 with unresolved TBDs in the decision table.
- All artifacts go in `~/.claude/projects/DSC/` — never write to the git repo.
- ADO attachments ALWAYS via subagent. Direct download crashes the main thread.
- ADO story descriptions are self-contained HTML — developers read them in ADO without needing analysis artifacts.
- Edge cases are assigned to stories, not tracked separately. No orphaned edge cases.
- When the user corrects an assumption, write the correction to the knowledge base immediately.
- Research artifacts are unique per feature — do not reuse across features.
- If a referenced doc doesn't exist yet, note what should be captured there and move on.
- If Phase 3 exceeds ~30 exchanges, flush to interim analysis-draft.md and restart the window.
- The deliverables are ADO user stories + knowledge base updates. Not specs, not code.
