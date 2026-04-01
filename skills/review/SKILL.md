---
name: review
description: Review the current branch's diff for bugs, security issues, and design problems. If a PR exists, also investigates unresolved reviewer comments. Accepts optional extension filters (e.g. `/review sol go`, `/review ts tsx`). Default is all changed files.
argument-hint: <extensions to filter by, e.g. "sol go" or "ts tsx">
disable-model-invocation: true
---

# Code Review Skill

You are an orchestrator reviewing a branch for bugs, security issues, and design problems — and investigating unresolved PR reviewer feedback when a PR exists.

## Context

!`~/.claude/skills/review/scripts/review-setup.sh $ARGUMENTS`

## Principles

- **You are an orchestrator.** Do NOT read code or explore the codebase directly — dispatch subagents for ALL investigation.
- **Parallel by default.** Dispatch review subagents concurrently — one per logical file group.
- **Language-aware analysis.** Use the file extensions from context to apply idiomatic checks for each language. Follow each language's conventions and known pitfalls.
- **Two independent streams.** Claude's code review and reviewer feedback investigation run as separate subagent pools. Neither influences the other during investigation — they merge at synthesis.

## Rules

- Include the Subagent Tooling Block (below) verbatim at the TOP of every subagent prompt.
- All Explore subagents MUST use `model: "sonnet"`.
- Never read source files yourself — always dispatch subagents.
- The full diff is already in context above. Use it for scoping, then dispatch subagents for deep analysis.

### Subagent Tooling Block

```
MANDATORY TOOL USAGE — Read this first:
- Use the Glob tool to find files (NEVER bash find, ls, or shell globbing)
- Use the Grep tool to search file contents (NEVER bash grep, rg, or awk)
- Use the Read tool to read files (NEVER bash cat, head, tail, or sed)
- The Bash tool must ONLY be used for running build/test commands
- WHY: Glob/Grep/Read require no permission approval and execute instantly. Bash file commands trigger permission prompts that block your execution.
```

---

## Phase 1 — Scope & Plan

1. **Read the diff** — already injected above. Read every line — additions, removals, and context.
2. **Identify review groups** — Partition changed files into logical groups (by directory/module). Keep related test files with their implementation. Aim for 2–5 groups; single-file PRs get one.
3. **Check for PR context** — If `PR_CONTEXT_START` is present in the injected context, note the unresolved threads. You will investigate them in Phase 3.
4. **Dispatch** — Move to Phase 2. If PR context exists, dispatch Phase 2 and Phase 3 concurrently.

---

## Phase 2 — Parallel Deep Review (Claude's Analysis)

Dispatch one **File Group Review Subagent** per group, in parallel. For functions, types, or modules referenced in the diff that live outside changed files, dispatch a **Cross-Reference Subagent** in parallel.

### File Group Review Subagent

Use `subagent_type: "Explore"`, `model: "sonnet"`. One per file group, parallel.

```
{Subagent Tooling Block}

You are reviewing a PR for bugs, security issues, and design problems.

## Your assigned files
{list of files in this group}

## Diff for these files
{paste the relevant diff chunks}

## Instructions

1. Read each changed file in full (not just the diff) to understand surrounding context.
2. For each changed function/method, trace the execution path from entry to exit.
3. Check for: logic errors, security issues, state consistency, error handling, missing validation, race conditions, resource leaks, breaking API changes, dead code, and missing test coverage.
4. Apply language-idiomatic checks — follow the conventions and known pitfalls of the language being reviewed.
5. Check interactions between files in this group — are changes consistent?
6. Check that test files (if present) actually cover the new/changed behavior.

## Output format

For each issue found:
- **File**: `path/to/file:line_number`
- **Severity**: Critical / High / Medium / Low
- **Description**: What's wrong and why it matters
- **Suggestion**: How to fix it

Also report:
- **Verified correct**: Non-obvious things you checked that are fine
- **Needs cross-reference**: Functions/types/modules referenced but not in your file group
```

### Cross-Reference Subagent

Use `subagent_type: "Explore"`, `model: "sonnet"`.

```
{Subagent Tooling Block}

Answer the following questions about functions, types, or modules referenced in a PR diff.

## Questions
{list of specific questions, e.g.:
- "What does `validateOrder()` in `src/utils/validation.ts` do? What are its preconditions and return values?"
- "How is `processQueue` called — is it safe to call concurrently?"
}

For each question:
- **Answer**: 1-3 sentences
- **Evidence**: file paths with line numbers
- **Implications**: edge cases, preconditions, or side effects the caller should know about
```

---

## Phase 3 — Reviewer Feedback Investigation (conditional)

**Skip this phase entirely if no `PR_CONTEXT_START` block is present in the injected context.**

This phase runs concurrently with Phase 2.

### Step 1 — Digest

Parse the injected PR review threads. Group by file. For each thread, produce a 1-line neutral summary of what the reviewer is asking — no judgment yet.

### Step 2 — Investigate

Dispatch parallel Explore subagents — one per file group. Use `subagent_type: "Explore"`, `model: "sonnet"`.

```
{Subagent Tooling Block}

You are investigating code around PR review comments to understand context — NOT fixing anything.

**File:** {path}

**Threads to investigate:**

{for each thread in this file:}
---
Thread: {thread_id}
Line: {line}
Reviewer asks: {neutral 1-line summary}
Comment: {body}
Diff context:
{diff_hunk}
---
{end for}

**Your task:**

1. Read the FULL current file.
2. For each thread, investigate:
   - What does the code actually do at this location? What's the broader context?
   - Is the reviewer's concern valid given the full picture? Or does surrounding code already handle it?
   - If the concern is valid, what would the minimal fix look like? Is it contained to this file or cross-file?
   - Are there patterns elsewhere in the codebase that inform the right approach? (search for similar code)
3. Do NOT make any edits. Investigation only.

**Output per thread:**

FINDING_START
thread: {thread_id}
current_behavior: {what the code actually does}
reviewer_valid: {true|false|partially}
evidence: {specific code references — file:line — supporting your assessment}
fix_complexity: {trivial|moderate|cross-file|none_needed}
recommended_action: {1-2 sentences on what should happen, or why no change is needed}
FINDING_END
```

---

## Phase 4 — Synthesize & Present

1. **Collect** all subagent findings from Phase 2 (Claude's review) and Phase 3 (reviewer feedback).
2. **Deduplicate** — if Claude and a reviewer flagged the same issue, merge them and note both sources.
3. **Cross-validate** — use cross-reference findings to confirm or dismiss issues. Use reviewer investigation findings to strengthen or challenge Claude's analysis and vice versa.
4. **Rank** by severity, then confidence.
5. **Present:**

```
## Review: <branch-name>

### Summary of Changes
<Brief description based on commits and diff>

### Claude's Review — Bugs / Issues Found

#### 1. **<Title>** (Critical / High / Medium / Low)
`file:line` — Description with code snippet.

**Recommendation**: How to fix it.

#### 2. ...

(If no issues found, say so explicitly — don't invent problems.)

### Claude's Review — Verified Correct
- Non-obvious things checked and confirmed fine, with file:line references.

{If PR context exists:}

### Reviewer Feedback (N unresolved threads)

#### Thread: `file:line` — <neutral summary>
- **Reviewer says:** <comment summary>
- **Investigation:** <what code actually does, is concern valid?>
- **Recommended action:** FIX / ALREADY_HANDLED / NEEDS_DISCUSSION
- **Evidence:** file:line references

{End if}

### Recommended Actions
1. [FIX] `file:line` — <description> (source: Claude / Reviewer @username)
2. [FIX] `file:line` — <description>
3. [DISCUSS] `file:line` — <question needing human input>
...

### Open Questions
- <anything ambiguous from either Claude's review or reviewer comments
  that needs human input before proceeding>
```

**Severity guide:**
- **Critical**: Data loss, security exploit, broken access control, corruption
- **High**: Incorrect behavior that will cause failures in production
- **Medium**: Edge cases, missing validations, design issues
- **Low**: Code quality, performance, minor design questions

### Observations
- Optional non-blocking suggestions, clearly marked as such.

---

## Phase 5 — Fix (on request)

Only if the user agrees with findings:
1. Implement fixes — one at a time, smallest change possible.
2. Run relevant tests after each fix.
3. Do NOT make changes beyond what was discussed — no drive-by refactors.
