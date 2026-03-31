---
name: pr-respond
description: Respond to PR review comments — digest, investigate, decide, execute, validate. Orchestrates subagents for all code work.
argument-hint: <pr-url>
disable-model-invocation: true
---

# PR Respond

Orchestration agent: understand PR comments → investigate code → decide with evidence → execute fixes → validate.

## Context

!`.claude/skills/pr-respond/scripts/fetch-pr-context.sh $0`

## Principles

- **Understand before judging.** Never classify a comment as "fix" or "skip" until you've investigated the code. Reviewers lack full context. So do you — until subagents report back.
- **You are an orchestrator.** NEVER read code or explore the codebase directly — dispatch subagents for ALL investigation and implementation. If the human challenges a decision and you need evidence, dispatch a subagent to gather it.
- **Humans gate around uncertainty, not between phases.** If investigation produces a clear answer, flow forward. If there's genuine ambiguity or a design tradeoff, stop and ask.
- **Minimal, surgical changes.** Fix what the comment asks. Don't refactor surrounding code, add docs, or "improve" things.

### Subagent Tooling Block

Copy verbatim as the first section of every subagent prompt that touches the filesystem:

```
MANDATORY TOOL USAGE — Read this first:
- Use the Glob tool to find files (NEVER bash find, ls, or shell globbing)
- Use the Grep tool to search file contents (NEVER bash grep, rg, or awk)
- Use the Read tool to read files (NEVER bash cat, head, tail, or sed)
- The Bash tool must ONLY be used for running build/test commands
```

---

## L1 — Digest

**Owner:** AI (autonomous) | **Output:** grouped summary presented to human

Parse the injected context. Group threads by file. For each thread, produce a 1-line neutral summary of what the reviewer is asking — no judgment on whether to fix yet.

Present to human:

```
### {file_path} ({N} threads)
- Thread {id} (L{line}): {neutral summary of what reviewer is asking}
- ...
```

Tell the human: *"I'll investigate the code around each of these before deciding what to do."*

**Flow:** Proceed to L2 immediately — no gate needed.

---

## L2 — Investigate

**Owner:** AI (autonomous) | **Output:** findings per file group

Dispatch parallel Explore subagents — one per file group. Use `subagent_type: "Explore"`, `model: "sonnet"`.

### Explore Subagent Prompt

```
{Subagent Tooling Block}

You are investigating code around PR review comments to understand context — NOT fixing anything.

**File:** {REPO_PATH}/{path}

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

**Gate:** Wait for all Explore subagents. Synthesize findings into L3.

---

## L3 — Decide

**Owner:** Human at uncertainty, AI otherwise | **Output:** approved action plan

Using investigation findings, classify each thread:

- **FIX** — Reviewer is right, evidence confirms the issue, fix is clear. *Cite the evidence.*
- **ALREADY_HANDLED** — Current code already addresses the concern. *Cite where.*
- **ASK** — Genuine ambiguity, design tradeoff, or conflicting signals. *State what's uncertain.*
- **SKIP** — Reviewer concern is not valid given full context, or is pure style/speculative. *Cite why.*

Present to human with evidence:

```
### Decisions

**FIX ({n}):**
- Thread {id} ({file}:L{line}): {what and why} — Evidence: {code reference}

**ALREADY_HANDLED ({n}):**
- Thread {id} ({file}:L{line}): {why no change needed} — Evidence: {code reference}

**SKIP ({n}):**
- Thread {id} ({file}:L{line}): {why skipping} — Evidence: {code reference}

**ASK ({n}):**
- Thread {id} ({file}:L{line}): {specific question for human}
```

**Gate:** Human must confirm. If human disagrees on any classification, dispatch a subagent to gather more evidence before changing your position — don't just flip.

---

## L4 — Execute

**Owner:** AI (autonomous) | **Output:** code changes

Launch parallel subagents — one per file with FIX threads. Use `subagent_type: "general-purpose"`, `model: "sonnet"`.

### Fix Subagent Prompt

```
{Subagent Tooling Block}

You are making targeted fixes for approved PR review comments on a single file.

**File:** {REPO_PATH}/{path}
**Repo language:** {language}

**Approved fixes:**

{for each FIX thread in this file:}
---
Thread: {thread_id}
Line: {line}
Comment: {body}
Investigation finding: {recommended_action from L2}
Human guidance: {any ASK answers that apply, or "none"}
Diff context:
{diff_hunk}
---
{end for}

**Instructions:**

1. Read the FULL current file.
2. Make the minimal fix for each thread. You have investigation context — use it.
3. Do NOT refactor, add comments, or change unrelated code.
4. You may ONLY edit {REPO_PATH}/{path}. No other files.
5. Run the language formatter after edits:
   - Go: gofmt -w {file}
   - TypeScript: bunx prettier --write {file}

**End your response with:**

RESULT_START
file: {path}
{for each thread:}
thread: {thread_id}
verdict: {FIXED|BLOCKED}
reason: {1-2 sentences}
{end for}
RESULT_END
```

**Gate:** Wait for all subagents.

---

## Validate + Report

1. **If any thread was FIXED**, run build and lint commands from the injected repo context.
2. **If build fails**, launch ONE remediation subagent. Re-run. If still failing, report to human.
3. **Collect BLOCKED threads** (cross-file changes). Present to human for guidance.

Present final summary:

```
### PR Review: {title}
**Threads:** {total} | Fixed: {n} | Already handled: {n} | Skipped: {n} | Blocked: {n}
**Build:** {PASS|FAIL|NO_EDITS}

| File | Thread | Line | Verdict | Summary |
|------|--------|------|---------|---------|
| ... | ... | ... | ... | ... |

{if BLOCKED:}
**Cross-file changes needed:**
- {file}: {description}
{end if}

Changes are NOT committed. Review with `git diff` and commit when ready.
```
