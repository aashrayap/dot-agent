# Morning Focus Review Contract Relocation: Research Pro Review Brief

## Reviewer Context

You are reviewing a dot-agent workflow/spec question. Assume access to this
Markdown packet and the remote dot-agent repository only. Do not assume access
to Ash's local filesystem. Machine-local context from `semi-stocks-2` is
summarized below because the misplaced planning artifact is untracked and not
available from the remote repository.

This packet is also a start-session spec for a future local session. The correct
repo for the next session is:

```text
/Users/ash/.dot-agent
```

Do not start in `semi-stocks-2` for this work except to delete or move the
misplaced untracked files after the dot-agent disposition is decided.

## Review Target And Mode

- Mode: product/spec critique and workflow-boundary review.
- Remote target: `3fd72084cbc6ecbf18c5f36b5a65576e0b581111`
- Base/comparison: current `main`; no implementation diff yet.
- Requested scrutiny: challenge whether the proposed "morning focus review"
  idea should become dot-agent behavior, remain a parked handoff, or be deleted
  as overfitted process work.

## Access Protocol

1. Confirm repo access: https://github.com/aashrayap/dot-agent
2. Use `Inline Evidence` as the minimum source of truth.
3. If repo access exists, use `Primary Raw URLs` below as source of truth for
   primary files.
4. Treat PR, branch, tree, and blob pages as context only.
5. If any primary raw URL fails, cite the exact URL and stop. Do not fall back
   to stale branch/cache state.

## Source And Access Policy

- Primary evidence: dot-agent repo paths, this packet, and the summarized
  local `semi-stocks-2` untracked artifact facts below.
- Web/external sources: not needed.
- Non-repo/local context: included in `Non-Repo Context Included`.
- Sensitive context check: no secrets, API keys, transcript contents, or
  private runtime logs are included.

## Primary Raw URLs

- https://raw.githubusercontent.com/aashrayap/dot-agent/3fd72084cbc6ecbf18c5f36b5a65576e0b581111/README.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/3fd72084cbc6ecbf18c5f36b5a65576e0b581111/skills/morning-sync/SKILL.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/3fd72084cbc6ecbf18c5f36b5a65576e0b581111/skills/focus/SKILL.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/3fd72084cbc6ecbf18c5f36b5a65576e0b581111/skills/execution-review/SKILL.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/3fd72084cbc6ecbf18c5f36b5a65576e0b581111/docs/handoffs/human-daily-loop-redesign.md

## Goal

- Decide what to do with a misplaced `morning-focus-review-contract` planning
  artifact currently sitting untracked in `semi-stocks-2`.
- Preserve any durable dot-agent workflow insight if it is worth keeping.
- Keep semi-stocks clean by removing or moving non-domain harness artifacts.
- Avoid silently changing `morning-sync` into a heavy forensic/session-memory
  reader if that contradicts the current human daily loop.

## General Direction

1. Treat `~/.dot-agent` as the source-of-truth repo for this idea.
2. Treat `semi-stocks-2` files as misplaced local context, not as canonical
   semi-stocks artifacts.
3. Keep `focus` as the only roadmap write gate.
4. Keep `execution-review` forensic unless a reviewed design explicitly adds a
   lightweight read-only intake to `morning-sync`.
5. Prefer a small parked handoff or issue-like artifact over immediate skill
   edits unless the design survives critique.

## Files To Review

Primary starting points, not hard boundaries:

- `README.md`
- `skills/morning-sync/SKILL.md`
- `skills/focus/SKILL.md`
- `skills/execution-review/SKILL.md`
- `docs/handoffs/human-daily-loop-redesign.md`

## Inline Evidence

`README.md` lines 92-95

```text
The normal day-start surface is the human roadmap, not project/session memory.
```

Explanation: this is the current top-level dot-agent position. The proposed
morning-focus idea pushes toward recent-session evidence in the morning loop,
so this sentence is the main contract to preserve or intentionally revise.

`README.md` lines 86-90

```text
Use `state/` for local operating memory:
- `state/collab/roadmap.md`
- `state/ideas/<slug>/`
- `state/tools/`
```

Explanation: current operating memory is local and gitignored. Any session
memory intake must respect that boundary and not require remote reviewers to
open private runtime logs.

`skills/morning-sync/SKILL.md` lines 15-21

```text
- Children: `focus` for roadmap mutations ...
- Reads state from: `~/.dot-agent/state/collab/roadmap.md` by default ...
- Writes through: `focus`/`roadmap.py` only when the user asks for an updating sync.
```

Explanation: current `morning-sync` already composes with `focus`, but only
reads the roadmap by default and does not own silent roadmap mutation.

`skills/morning-sync/SKILL.md` lines 44-50

```text
Always read:
- `~/.dot-agent/state/collab/roadmap.md`

Do not inspect gitignored legacy project/session state during the normal
morning path. If the user needs historical context, ask for the explicit file
or artifact they want reviewed.
```

Explanation: this directly conflicts with making recent Claude/Codex session
memory an automatic morning input. A design can still add explicit opt-in
behavior, but it should not erase this guard casually.

`skills/focus/SKILL.md` lines 16-22

```text
- Parent: `morning-sync` for day-start orchestration.
- Reads state from: `~/.dot-agent/state/collab/roadmap.md` by default ...
- Writes through: `skills/focus/scripts/roadmap.py` for roadmap mutations ...
```

Explanation: `focus` is already the write gate for the day board. The proposed
workflow's "roadmap mutations proposed" section should hand off to `focus`
rather than mutate state.

`skills/focus/SKILL.md` lines 34-38

```text
Read `~/.dot-agent/state/collab/roadmap.md` every time ...
Do not inspect legacy project/session state unless the user points to a
specific historical artifact.
```

Explanation: `focus` has the same guard against default session-state
inspection. Any new intake design must decide whether this guard remains.

`skills/execution-review/SKILL.md` lines 8-16

```text
- Parent: forensic execution review ...
- Reads state from: Codex/Claude session logs ...
- Writes through: execution-review report/history files only.
- Hands off to: `daily-review` ... `spec-new-feature`, `focus`, or `review`
  only as recommended follow-up surfaces.
```

Explanation: `execution-review` already owns session-log evidence and hands
recommendations elsewhere. The proposed morning-focus design should not
duplicate this forensic layer without a narrow reason.

`skills/execution-review/SKILL.md` lines 61-64

```text
Cluster sessions into logical workstreams ...
If closure, recap, or roadmap-drainage work is needed, recommend handoff to
`daily-review` instead of mutating state here.
```

Explanation: this already contains the strongest reusable primitive for
"what has Ash actually been working on?" but keeps mutation outside the
forensic review.

`docs/handoffs/human-daily-loop-redesign.md` opening section

```text
Status: live skill-contract handoff implemented for `morning-sync`, `focus`,
`daily-review`, and the roadmap helper. State migration remains future work.

Decision: Move dot-agent's day-start and day-end workflow toward a
human-readable daily board ... while keeping dot-agent's richer forensic
review work out of the normal morning/focus path.
```

Explanation: the current human daily loop redesign intentionally separated
normal morning/focus work from richer forensic review. The new idea may be a
refinement, but it should be reviewed against that existing decision.

Misplaced local artifact summary, originally in
`semi-stocks-2/docs/artifacts/morning-focus-review-contract/00_summary.md`

```text
Purpose: Shape a merged day-start workflow where `morning-sync` reads recent
Codex and Claude work, highlights what Ash has actually been working on, and
then asks whether to continue, reprioritize, park, promote, or drop work.

Current Decision:
- Prefer `morning-sync` when the question is "what should I do today?"
- Prefer `focus` when Ash already knows the change and wants to mutate the
  roadmap.
- Prefer `execution-review` when the question is forensic.
- Proposed merge: `morning-sync` can run a lightweight execution-review intake
  before producing the morning contract, but `focus` remains the only roadmap
  write gate.

Checkpoint: Research is complete. Next step is design: decide the exact
morning-sync contract change, recent-work window policy, and whether to add a
lightweight execution-review summarizer helper.
```

Explanation: this is the actual idea to evaluate. It is useful harness thinking
but is in the wrong repository and currently untracked.

Misplaced local files to delete or move after disposition

```text
semi-stocks-2/docs/artifacts/morning-focus-review-contract/
semi-stocks-2/docs/diagrams/morning-focus-review-current-vs-proposed.excalidraw
semi-stocks-2/docs/diagrams/morning-focus-review-current-vs-proposed.png
```

Explanation: these are not semi-stocks domain artifacts. They should not remain
in the canonical semiconductor research repo.

## Review Breadth

Inspect adjacent skill docs, scripts, setup behavior, and existing handoffs if
needed. Keep findings tied to the day-start workflow and repo-boundary question.
Do not do a broad redesign of every daily-loop skill unless a primary finding
requires it.

## Non-Repo Context Included

- The misplaced artifact was created locally in `semi-stocks-2` on
  2026-04-21 around 02:45 CDT.
- The artifact is untracked in `semi-stocks-2`.
- A separate untracked visual exists at
  `semi-stocks-2/docs/diagrams/morning-focus-review-current-vs-proposed.*`.
- Current `semi-stocks-2` work should stay focused on semiconductor research,
  Signal Desk, and automation outputs.
- Current dot-agent worktree has unrelated dirty files:
  `claude/settings.json` and `codex/config.toml`. Treat them as out of scope.

## Assumptions And Blind Spots

Assumptions to falsify:

1. The morning-focus artifact belongs in dot-agent - current evidence: it
   references `morning-sync`, `focus`, `execution-review`, and roadmap mutation
   policy - disprove if semi-stocks has an active repo-specific morning review
   contract that should own it.
2. The idea should not be implemented directly yet - current evidence: it
   conflicts with current "no session-state in normal morning path" rules -
   disprove if current user workflow needs immediate opt-in recent-work intake.
3. A small parked handoff may be enough - current evidence: there is no approved
   design and the existing human daily loop intentionally separates forensic
   review from morning sync - disprove if the artifact contains decisions that
   are already accepted and only need relocation.

Reviewer blind spots:

- Reviewer cannot inspect the untracked local artifact unless using the inline
  summary above.
- Reviewer cannot run local Codex/Claude session-memory scripts.
- Reviewer cannot see private roadmap contents unless summarized here.

## What Changed

No implementation has changed yet. This handoff is the proposed next-session
starting point.

Recommended local session flow:

1. Start in `/Users/ash/.dot-agent`.
2. Read this handoff plus the primary skill docs listed above.
3. Decide one of:
   - delete the misplaced artifact entirely
   - copy a short summary into `docs/handoffs/` as a parked design note
   - open a proper `spec-new-feature` or handoff for a reviewed
     `morning-sync` opt-in recent-work intake
4. If keeping the idea, preserve these constraints:
   - `focus` remains the roadmap write gate
   - `execution-review` remains forensic
   - `morning-sync` stays lightweight by default
   - recent-session intake is opt-in or clearly bounded
5. After disposition, clean `semi-stocks-2` untracked files listed above.
6. Run the narrow relevant gate:
   - if only deleting misplaced files: `git -C /Users/ash/Documents/2026/semi-stocks-2 status --short`
   - if changing dot-agent docs only: `git diff --check`
   - if changing dot-agent skills/config: `~/.dot-agent/setup.sh --check-instructions`

## Validation Already Run

- `git -C /Users/ash/.dot-agent status --short`: showed unrelated modified
  `claude/settings.json` and `codex/config.toml`.
- `git -C /Users/ash/Documents/2026/semi-stocks-2 status --short`: showed the
  misplaced morning-focus artifact and diagram as untracked.
- `git diff --check`: should be run after this handoff is written.

## Known Out Of Scope

- Fixing `claude/daily-signals` in `semi-stocks-2`.
- Editing `hourly-market-intel` trigger setup.
- Changing dot-agent runtime config in `claude/settings.json` or
  `codex/config.toml`.
- Broad execution-review scoring or weekly retrospective.
- Moving private local roadmap/session state into tracked files.

## Findings Intake Plan

Returned findings should be triaged into:

- fix now: update this handoff or create a small dot-agent design note before
  cleaning semi-stocks.
- backlog: add a roadmap/focus row for a reviewed morning recent-work intake.
- local verification: any recommendation requiring script checks or runtime
  memory inspection.
- reject with reason: record in the eventual cleanup commit or chat receipt.

## Review Tasks

Please review for:

1. Is the correct repo for item 1 definitely `dot-agent`, and is the proposed
   cleanup path safe?
2. Should the morning-focus idea be deleted, parked, or turned into a reviewed
   dot-agent feature?
3. If it becomes a feature, what is the narrowest contract that preserves the
   current `morning-sync` / `focus` / `execution-review` boundaries?
4. Does the proposed local session flow risk losing useful context or leaking
   private/session state into tracked docs?

## Bonus Scope

If time allows, briefly check whether existing `daily-review` or
`execution-review` already has a better place for this idea. Keep bonus findings
separate from primary findings.

## Desired Reviewer Output

Lead with findings. For each finding include:

- severity: blocker, high, medium, low
- file/path
- issue
- why it matters
- suggested fix

If there are no blocking findings, say that explicitly and then recommend one
of: delete, park as handoff, or promote into a focused dot-agent spec.
