---
name: review
description: Review the current branch's diff for bugs, security issues, and design problems. If a PR exists, also investigates unresolved reviewer comments. Accepts optional extension filters (e.g. `/review sol go`, `/review ts tsx`). Default is all changed files.
argument-hint: <extensions to filter by, e.g. "sol go" or "ts tsx">
disable-model-invocation: true
---

# Code Review Skill

## Composes With

- Parent: user code-review request.
- Children: GitHub plugin workflows when PR metadata, CI, or unresolved review comments exceed local scripts; `excalidraw-diagram` only when a broad review needs a durable architecture or workflow visual.
- Uses format from: `excalidraw-diagram` for high-level review maps when useful; line-specific findings remain text-first.
- Reads state from: git diff, changed files, PR context when available, `docs/UBIQUITOUS_LANGUAGE.md` when present, and repository tests/docs.
- Writes through: none by default; review comments only when explicitly requested.
- Hands off to: `github:gh-address-comments` for unresolved review threads and `github:gh-fix-ci` for failing CI.
- Receives back from: GitHub plugin context when used.

When delegation is explicitly authorized, use subagents for territory, change,
and verification passes. Otherwise perform the same staged review locally.

For narrow code findings, cite exact files and lines without forcing a diagram.
For broad contract, workflow, or architecture reviews, add or link a diagram
when it makes the reviewed shape easier to understand.

For docs, instructions, architecture, domain-model, or broad workflow changes,
read `docs/UBIQUITOUS_LANGUAGE.md` when present and flag terminology drift
when changed files introduce aliases, obsolete terms, or conflicting meanings.

## Core Design

- **Decontamination.** Track A (territory) never sees the diff. Track B (change) never sees surrounding code. They meet at cross-examination.
- **Agents self-scope.** Don't partition files. Agents receive starting points and follow dependencies wherever they lead.
- **Evidence standard.** Every finding must cite file:line with specific reasoning, not vibes.

## Rules

- All subagents: `subagent_type: "Explore"`, `model: "sonnet"`.
- Prefix every subagent prompt with the Tooling Block below.
- Role mapping: territory/change/reviewer tracks use Explorer; requested fixes
  use Worker / Implementor; post-fix validation uses Gate / Verifier.

### Tooling Block

```
MANDATORY: Use Glob (not find/ls), Grep (not grep/rg), Read (not cat/head/tail). Bash only for build/test commands or git diff. Glob/Grep/Read need no permission and execute instantly.
```

---

## Phase 1 — Scope

1. If the user specified a repo path, `cd` there first.
2. Run via Bash: `~/.claude/skills/review/scripts/review-setup.sh`
   — Returns: branch info, MERGE_BASE, changed file paths, diff stats, commits, PR_URL (if any). No file content or diffs.
3. If user specified extension filters (e.g. `go`, `ts tsx`), filter the changed file list.
4. Note PR_URL — determines whether Track C runs.

---

## Phase 2 — Parallel Investigation

Launch all tracks concurrently. A and B always run. C only if PR exists.

### Track A: Territory

**Does not see the diff, commits, or PR description. Only gets the list of changed file paths.**

Prompt:
```
{Tooling Block}

Investigate these source files to understand how they work. Do not run git diff or read commit messages.

## Starting files
{changed file paths only}

## Instructions
1. Read every starting file in full.
2. Follow references outward: callers, type definitions, shared state accessors, test files. Trace as deep as needed to understand the full contract surface.
3. For each file report: purpose, contracts (pre/postconditions, invariants), upstream/downstream dependencies, patterns, edge cases, shared state (and how it's protected).
4. End with cross-cutting observations: patterns spanning files, cross-module invariants, concurrency/state/lifecycle contracts.
```

### Track B: Change Analysis

**Sees only the raw diff. Does not read source files.**

Prompt:
```
{Tooling Block}

Analyze a code diff without reading any source files. Work only from the diff.

Run via Bash: git diff {MERGE_BASE}...HEAD
{If extension filters: Only analyze hunks matching: {extensions}}

## Instructions
1. Per file: what changed, inferred intent, assumptions about surrounding code.
2. Cross-file interactions: dependency changes, signature changes, type propagation.
3. Risk flags: removed guards, changed control flow, changed error handling, new I/O.
4. End with a numbered list of "Assumptions requiring validation" — each assumption the change makes that can't be verified from the diff alone, with file:line ranges.
```

### Track C: Reviewer Feedback (PR only)

Skip if no PR_URL.

1. Run via Bash: `~/.claude/skills/review/scripts/fetch-pr-context.sh`
   If no unresolved threads, skip this track.
2. Summarize each thread in one neutral line.
3. Dispatch one Explore subagent:

```
{Tooling Block}

Investigate code around PR review comments. Do not fix anything.

{per thread:}
---
Thread: {id} | File: {path} | Line: {line}
Reviewer asks: {1-line summary}
Comment: {body}
Diff hunk: {diff_hunk}
---

For each thread: read the full current file, determine if the reviewer's concern is valid given the full picture, check if surrounding code already handles it, note relevant codebase patterns. Report per thread: thread id, file, line, concern summary, current behavior, valid (true/false/partially), evidence (file:line refs).
```

---

## Phase 3 — Cross-Examination

After Phase 2 completes, dispatch one Explore subagent that sees all track outputs for the first time.

Prompt:
```
{Tooling Block}

Cross-examine a code change against independently gathered evidence. These inputs were produced in isolation.

## Territory findings (gathered without seeing the diff)
{Track A output}

## Change findings (gathered without seeing surrounding code)
{Track B output}

{If Track C ran:}
## Reviewer findings
{Track C output}
{End if}

## Instructions
1. **Validate assumptions.** For each numbered assumption from the change analysis, check territory findings. Verdict: VALID (cite file:line) / INVALID (what does territory say?) / UNVERIFIABLE (read the code to resolve).
2. **Check invariants.** Does the change respect every contract/pattern documented in territory? Violations are findings.
3. **Cross-file interactions.** Do territory findings confirm the change's cross-file dependencies work correctly?
4. **Reviewer concerns (if applicable).** Does territory evidence support or contradict each reviewer? Did the change analysis reveal context the reviewer missed?
5. **New issues.** Problems visible only by combining both perspectives (e.g., change is internally consistent but violates a territory contract).

For each finding: cite severity (Critical/High/Medium/Low), evidence from both tracks (file:line), and why neither track could catch it alone.
```

---

## Phase 4 — Synthesize

Orchestrator produces final output directly (no subagents). Collect, deduplicate, rank by severity then confidence.

**Severity guide:** Critical = data loss, security, corruption. High = incorrect behavior in production. Medium = edge cases, missing validation, design issues. Low = quality, performance.

### Output Format

```
## Review: <branch-name>

### What This Change Does
<1-3 sentences from Track B's analysis>

### Summary of Territory
<Key code areas, contracts, and invariants from Track A>

### Issues Found

#### 1. **<Title>** (Severity)
`file:line` — Description.
**Territory**: what the code expects
**Change**: what the diff does
**Evidence**: from cross-examination
**Recommendation**: how to fix

(If no issues: say so explicitly. Don't invent problems.)

### Assumptions Validated
- Non-obvious validations worth noting, with evidence.

### Verified Correct
- Non-obvious things confirmed fine, with file:line.

{If PR:}
### Reviewer Feedback ({N} threads)
Per thread: what reviewer says, what territory says, cross-examination verdict (FIX / ALREADY_HANDLED / NEEDS_DISCUSSION), evidence.
{End if}

### Recommended Actions
1. [FIX] `file:line` — description (source)
2. [DISCUSS] `file:line` — question needing human input

### Open Questions
- Anything ambiguous needing human input.

### Observations
- Optional non-blocking suggestions.
```

---

## Phase 5 — Fix (on request only)

For each agreed fix, dispatch one opus subagent with: what to change (files, additions, removals), the relevant finding with evidence, territory contracts to preserve, and a verify command. Include `Modify: {files}` and `Never touch: {out of scope files}`.

After all fixes: run relevant tests or a Gate / Verifier pass over the changed
files. No drive-by refactors.
