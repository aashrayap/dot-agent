---
name: handoff-research-pro
description: Create a single Markdown handoff packet for ChatGPT Research Pro or another remote-only external reviewer. Use when the user asks to package context, summarize goals/direction, prepare an outside review brief, or hand off local work where the reviewer has repo access but not this machine/runtime.
---

# Handoff Research Pro

## Composes With

- Parent: user request to package context for ChatGPT Research Pro or another remote-only reviewer.
- Children: `review` for severity-first reviewer output, `compare` for branch/file comparisons, and `excalidraw-diagram` when the handoff needs a durable visual.
- Uses format from: `review` for finding-oriented output expectations and existing `docs/handoffs/` packets for durable handoff shape.
- Reads state from: current chat intent, git status, branch, git diff, changed files, validation output, repo docs, and any explicitly relevant external/local context.
- Writes through: `docs/handoffs/<slug>-research-pro-review.md`.
- Hands off to: external reviewer/model via the generated Markdown packet.
- Receives back from: reviewer findings pasted into chat or saved as follow-up handoff.

Create one portable review brief that gives an external model enough context to
review the change without access to this machine. The packet should point to
repo files where possible and inline any important non-repo context.

## Review Gate Thesis

Use this as a selective external critique gate, not as a default step for every
spec or diff. The leverage comes from independent synthesis over a strong,
portable packet; do not justify the gate by model price alone.

Best fits:

- after `idea` when product, strategy, or external assumptions need
  falsification before code-grounded planning
- during `spec-new-feature` before design or task artifacts become execution
  direction
- before merge for instruction-heavy, architecture-heavy, migration-heavy, or
  easy-to-rationalize changes

Skip for small mechanical fixes, formatting, or changes where local runtime and
test access are the main evidence.

## Core Metrics

- Portable: repo-relative paths are preferred, but non-repo/local context is
  allowed when relevant. If the reviewer cannot access it remotely, include the
  important facts directly in the handoff file.
- Scoped but not boxed in: list primary files as starting points, not hard
  boundaries. Tell the reviewer to inspect adjacent code/docs when needed.
- Complete: include review target and mode, source/access policy, goal,
  direction, changed files, what changed, assumptions to falsify, validation,
  risks, review questions, desired output format, and findings intake plan.
- Evidence-backed: map claims to files, diffs, commands, chat-derived intent,
  or explicitly inlined local context.
- Reviewable: ask concrete questions and requested finding format; avoid
  generic "thoughts?" prompts.
- Composable: preserve relevant `## Composes With` contracts and call out
  related skills or workflows.
- Token-aware: summarize diffs and point to files; do not paste huge patches
  unless remote access cannot reconstruct the necessary context.
- Source-aware: say whether external web/source lookup is allowed, required, or
  out of scope; for repo review, treat the repo and packet as primary evidence.
- Ref-pinned: for GitHub remote reviews, include immutable commit SHAs and
  pinned raw file URLs for primary evidence. PR, branch, tree, and blob pages
  may be helpful context, but they must not be the only source of truth.
- Handoff-durable: write one Markdown artifact under `docs/handoffs/`.
- Gate-visible: record validation commands, pass/fail status, and known
  warnings or unverified gaps.

## Workflow

1. Inspect current state:
   - `git status --short`
   - current branch
   - `git diff --stat`
   - changed filenames
   - relevant validation output already run in this session
2. Read enough changed files and nearby docs to understand intent. Do not treat
   changed files as the full review boundary when adjacent code matters.
3. Separate context into:
   - primary review starting points
   - broader codebase areas the reviewer may inspect
   - important local/external facts to inline
   - source/access policy, including sensitive context checks
   - immutable refs and raw URLs for primary remote evidence
   - assumptions to falsify and reviewer blind spots
   - validation evidence
   - unrelated dirty files or out-of-scope work
   - where accepted findings should be routed next
4. Create or update `docs/handoffs/<slug>-research-pro-review.md` from
   `assets/research-pro-brief.template.md`.
5. Keep all paths repo-relative unless the path itself is part of the issue.
   For non-repo paths, summarize the needed facts so the handoff remains
   self-contained.
6. Ask for findings-first reviewer output with severities, paths, issue,
   impact, and suggested fix.
7. Run `git diff --check`.

## Packet Rules

- Use `Files To Review` for primary starting points.
- Add `Review Breadth` to explicitly allow broader repo inspection.
- Add `Review Target And Mode` so the reviewer knows the exact ref and lens.
- Add `Access Protocol` for remote GitHub reviews: confirm repo access, use
  pinned raw URLs as primary evidence, and fail closed if any primary raw URL
  cannot be fetched.
- Add `Primary Raw URLs` for every primary file when the review depends on
  remote GitHub access.
- Add `Source And Access Policy` so web search, repo scope, local facts, and
  sensitive-context handling are explicit.
- Add `Assumptions And Blind Spots` to focus critique on falsification and
  prevent false certainty about local/runtime facts.
- Add `Non-Repo Context Included` when local/runtime/external facts matter.
- Add `Known Out Of Scope` for unrelated dirty files and warnings.
- Add `Findings Intake Plan` so returned findings can become fixes, backlog
  rows, PR notes, feature tasks, or rejected-with-reason decisions.
- Add `Bonus Scope` only when the user wants opportunistic wider audit.
- Do not create multiple docs unless the handoff spans multiple independent
  review tracks.
- Do not require access to runtime homes, machine-local state, browser tabs, or
  private files unless their essential facts are quoted or summarized in the
  packet.
- Do not let the reviewer fall back to stale PR, branch, tree, or blob pages
  when pinned raw URLs fail. Tell them to report the exact failed URL and stop.

## Remote Review Lint

Before finishing a GitHub remote-review packet, check:

- primary evidence includes a commit SHA, not only a branch or PR URL
- every primary file has a pinned raw URL when the reviewer may use a browser
- dynamic PR/tree/blob links are labeled as context, not source of truth
- packet says what to do when a URL fails
- local/runtime facts needed for review are inlined in the packet
- unrelated dirty files are named as out of scope

## Output Path

Default slug:

```text
docs/handoffs/<topic>-research-pro-review.md
```

Use the user's requested path when provided.

## Final Response

Return the handoff file path, whether `git diff --check` passed, and any gaps
that remain for the external reviewer.
