---
name: review
description: Review current branch, diff, or PR for bugs, regressions, contract violations, and unresolved reviewer comments. Defaults to evidence-first cross-exam review.
---

# Review

Use this when the user asks for a code review, PR review, diff review, or wants unresolved reviewer comments checked against the current code.

## Quick Start

Run `scripts/review-setup.sh [ext ...]` first.

Use `scripts/fetch-pr-context.sh` when the repo has an open GitHub PR and reviewer comments matter.

## Modes

### Cross-Exam Review

This is the default unless the user explicitly asks for a lightweight review.

Run three staged passes:

1. Territory pass
   - Read the changed files and their dependencies.
   - Identify contracts, invariants, and important edge cases.
2. Change pass
   - Inspect the diff.
   - List risky assumptions, behavior changes, removed guards, and cross-file implications.
3. Synthesis pass
   - Compare the territory expectations to the actual diff.
   - Report mismatches, broken assumptions, and reviewer-thread verdicts.

### Standard Review

Use this only when the diff is tiny or the user explicitly wants a quick pass.

Inspect the changed code directly and report findings first, with severity and evidence.

## PR Thread Arbitration

If `scripts/review-setup.sh` reports a `PR_URL`, run `scripts/fetch-pr-context.sh`.

For each unresolved thread, decide whether the concern is:

- valid
- already handled
- outdated
- still ambiguous

Every verdict needs code evidence.

## Output Contract

- findings first
- severity ordered
- file:line evidence
- explicit "no findings" when none exist

Optional sections:

- validated assumptions
- reviewer thread verdicts
- open questions

## Fixes

If the user asks for fixes after the review:

- change only the agreed areas
- preserve documented contracts
- rerun the most relevant verification
- avoid drive-by refactors
