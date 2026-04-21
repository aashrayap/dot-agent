---
status: completed
feature: unified-workflow-morning-sync
---

# Research: unified-workflow-morning-sync

## Flagged Items

### F1. PR miss has two causes, not one

Answer: The normal skill path currently requires `recent-work-summary.py
--skip-prs`, so PR lookup is deliberately bypassed. When the helper is run
without `--skip-prs`, it uses local `gh`; in this session `gh` existed but
failed to connect to `api.github.com`. The Codex GitHub connector still returned
recent PRs for both repositories, so local helper unavailability should not be
reported as "no PRs".

Evidence:
- `skills/morning-sync/SKILL.md:47-48` requires reading the helper with
  `--skip-prs`.
- `skills/morning-sync/scripts/recent-work-summary.py:351-355` returns a
  skipped state for `--skip-prs` or missing `gh`.
- Helper smoke run without `--skip-prs` returned GitHub connection errors for
  `.dot-agent` and `semi-stocks-2`.
- Codex GitHub connector returned recent `dot-agent` merged PRs and a current
  open `semi-stocks-2` PR.

Confidence: high.

Conflicts: The skill text says the helper should check recent PRs where
available, but the always-read input currently disables that path.

Open item: deterministic scripts cannot call the Codex GitHub connector; the
skill contract needs a clear fallback rule for assistant-side external signals.

### F2. Recent-work noise is admitted by broad tertiary-window rules

Answer: The helper includes today, yesterday, 2-3 day secondary context, and
4-8 day tertiary context, then renders up to eight `User Decides` entries with
no minimum evidence threshold and no disposable-session filter. That is how a
4-day-old 1-minute alias session and smoke-test one-liners reached the morning
packet.

Evidence:
- `recent-work-summary.py:201-215` includes tertiary sessions from 4-8 days ago.
- `recent-work-summary.py:218-227` loads and sorts all sessions inside that
  band, capped only by global session limit.
- `recent-work-summary.py:523-530` adds every non-roadmap stream with sessions
  to `user_decides`.
- `recent-work-summary.py:571-574` renders the first eight user-decides rows.

Confidence: high.

Conflicts: Morning-sync says it should prefer current momentum and avoid
padding, but the helper currently supplies low-value rows without an
actionability filter.

Open item: decide exact thresholds for showing older untracked work.

### F3. Current commitments only include active-like statuses

Answer: `current_commitments` excludes `Queued` rows, even when a queued row is
the only explicit roadmap commitment. This caused the initial morning output to
say no in-progress commitments while `semi-stocks-2` was clearly queued on the
roadmap.

Evidence:
- `recent-work-summary.py:532-535` includes only `in progress`, `review`,
  `needs review`, `waiting`, `follow-up`, and `blocked`.
- Roadmap row `semi-stocks-2` has status `Queued`.

Confidence: high.

Open item: queued rows should be shown as commitments but not necessarily
treated as primary focus ahead of in-progress rows.

### F4. Open-gate state is too coarse for long workstreams

Answer: A roadmap stream becomes `open gate` when any recent session had edits
and zero verifications. It does not check whether later sessions verified the
same workstream, whether the unverified session was tiny, or whether the
session is relevant to the current roadmap task.

Evidence:
- `recent-work-summary.py:410-416` marks a roadmap stream `open gate` when any
  session has `edits > 0` and `verifications == 0`.
- Current helper output marks both `dot-agent` and `semi-stocks-2` as open
  gates across large multi-session streams.

Confidence: medium-high.

Open item: better gate logic needs session-level verification ordering or a
lighter label such as `has verification risk`.

## Findings

### Codebase

Q: Where does `morning-sync` force `--skip-prs`?

Answer: The skill input contract does. The helper itself only skips when the
flag is passed, but `morning-sync/SKILL.md` says to always read
`recent-work-summary.py --skip-prs`.

Evidence: `skills/morning-sync/SKILL.md:45-49`;
`skills/morning-sync/scripts/recent-work-summary.py:85-92`.

Confidence: high.

Q: What inputs classify workstreams, timestamps, evidence, and roadmap
membership?

Answer: Roadmap membership comes from `Active Projects` rows. Workstream name
comes from roadmap project name in the session label, then git root name or cwd
basename. Timestamps are mapped into local-day bands. Evidence is session count,
runtime count, wall time, optional PR count, and roadmap presence.

Evidence: `recent-work-summary.py:118-135`, `170-188`, `201-227`,
`230-250`, `450-455`.

Confidence: high.

Q: What thresholds suppress old/tiny/smoke sessions?

Answer: None beyond the 9-day local calendar window and global session cap.
There is no wall-time minimum, session-count minimum, label denylist, or
actionability scoring before `User Decides` rendering.

Evidence: `recent-work-summary.py:201-227`, `487-530`, `571-574`.

Confidence: high.

Q: How can roadmap rows map to repositories?

Answer: Current helper maps repositories only from session cwd git roots. It
does not parse roadmap `Link` cells as possible local repo paths. `remote_repo`
can turn a git root into `owner/name`, so the missing piece is adding roadmap
link paths into each roadmap stream's repo set when they resolve to git roots.

Evidence: `recent-work-summary.py:148-167`, `251-253`, `326-348`,
`356-360`; roadmap row links include `/Users/ash/Documents/2026/semi-stocks-2`
and artifact path under `/Users/ash/.dot-agent`.

Confidence: high.

Q: Which helper owns roadmap mutation?

Answer: `focus/scripts/roadmap.py` owns section-aware roadmap writes. The add
path updates frontmatter, normalizes status, inserts into the requested
section, and preserves table shape.

Evidence: `focus/scripts/roadmap.py:279-320`.

Confidence: high.

### Docs

Q: What do current contracts say about PRs and recent evidence?

Answer: Morning-sync is allowed to use lightweight recent-work intake and
optional PR status, but its always-read command disables PR lookup. It must keep
raw session internals hidden and route writes through focus.

Evidence: `morning-sync/SKILL.md:18`, `45-53`, `84-96`, `159-170`.

Confidence: high.

Q: Where should repo mappings or local paths live?

Answer: Runtime reference says `state/` is gitignored machine-local state, while
tracked config should avoid private context and machine-local overrides. For
this feature, tracked defaults should infer from roadmap links and git remotes;
any persistent custom repo map should be state, not tracked config.

Evidence: `docs/harness-runtime-reference.md` says `state/` is gitignored local
state and tracked config should avoid private/machine-local context.

Confidence: high.

Q: Is there already an improvement tally pattern?

Answer: Existing feature artifacts use `00_summary.md` as the durable landing
page. The current tally can live there without creating a separate workflow.

Evidence: `spec-new-feature` response contract and existing
`docs/artifacts/morning-focus-review-contract/00_summary.md`.

Confidence: high.

### Patterns

Q: How do skills separate day-start summary from forensic review?

Answer: Morning-sync consumes compressed recent work and hides session IDs;
execution-review owns forensic scoring, transcript inspection, raw sessions,
and detailed Hermes findings.

Evidence: `morning-sync/SKILL.md:50-56`, `167-169`;
`execution-review/SKILL.md` Morning Intake Boundary.

Confidence: high.

Q: How do scripts represent unavailable external signals?

Answer: The helper currently returns string notes such as `PR check skipped by
flag`, `gh not found`, or command error text. Rendering then still uses a
combined "No open PRs found, or PR lookup skipped/unavailable" line.

Evidence: `recent-work-summary.py:351-370`, `590-608`.

Confidence: high.

Q: How do roadmap helpers keep updates reversible?

Answer: They mutate only named sections, update `last_touched`, normalize
statuses, and provide add/status/drop actions rather than rewriting the whole
board ad hoc.

Evidence: `focus/scripts/roadmap.py:292-320` and status/drop helpers nearby.

Confidence: high.

### External

Q: What GitHub access exists in Codex desktop?

Answer: This session has a GitHub connector that returned recent PRs for
`aashrayap/dot-agent` and `aashrayap/semi-stocks-2`. Local shell also has
`/usr/local/bin/gh`, but helper PR lookup failed to connect to GitHub.

Evidence: connector calls returned latest user PRs; shell `which gh` returned
`/usr/local/bin/gh`; helper run returned `error connecting to api.github.com`.

Confidence: high.

Q: What failure modes should PR lookup expect?

Answer: At minimum: deliberately skipped by flag, `gh` missing, network/API
connectivity failure, non-GitHub repo, no open PRs, and connector-only signal
available outside the helper.

Evidence: helper code and pre-fix live runs produced skipped, not-GitHub, and
network-failure states.

Confidence: high.

### Cross-Ref

Q: Which current rows should be visible by default?

Answer: Roadmap rows should stay visible. Among untracked rows, `tracker`
belongs in `User Decides` because it is today and non-trivial. The old alias
row and smoke-test one-liners should be suppressed from the normal morning
packet. The `2026` row is ambiguous: high wall time, 2 days old, but likely a
workspace/container label rather than a project.

Evidence: helper output after adding `dot-agent` row; filtering rules above.

Confidence: medium.

Q: What minimal PR summary fits current state?

Answer:
- `dot-agent`: no open PRs in sampled user PRs; recent merged workflow/handoff
  changes exist.
- `semi-stocks-2`: one open PR requiring awareness; recent merged Signal Desk
  docs/reader/canonical work exists.

Evidence: Codex GitHub connector PR sample for both repos.

Confidence: high.

Q: What should morning-sync say for skipped vs empty PR lookup?

Answer: It should distinguish:
- `Skipped`: PR lookup deliberately disabled.
- `Unavailable`: attempted lookup failed or auth/network missing.
- `None open`: lookup succeeded and no open PRs matched.
- `Summary`: open/recent merged counts and attention line.

Evidence: current renderer collapses these at `recent-work-summary.py:604-608`.

Confidence: high.

## Patterns Found

- Roadmap remains the control plane; recent evidence only informs triage.
- User-facing morning output should compress, not enumerate.
- External signals must be labeled by source and availability.
- Deterministic helper scripts should return structured states; skill text can
  describe assistant-side connector fallback when available.
- Tertiary historical context is useful for continuity but harmful when shown
  as equal-weight `User Decides` rows.

## Core Docs Summary

- `morning-sync/SKILL.md`: owns day-start summary, must read roadmap and recent
  evidence, should keep PRs concise, and must not mutate roadmap silently.
- `focus/SKILL.md`: owns roadmap writes and selected-stream updates.
- `execution-review/SKILL.md`: owns forensic session review; morning-sync may
  consume only lightweight summaries.
- `harness-runtime-reference.md`: tracked config should avoid private local
  state; machine-local persistent state belongs under `state/`.
- Prior `morning-focus-review-contract` artifacts already implemented the first
  version of this workflow; this feature is a signal-quality follow-up.

## Resolved During Execution

- `User Decides` now shows untracked work only when it is current, repeated, or
  at least 15 minutes of wall time; stale/smoke rows are counted as omitted.
- Helper PR lookup now queries `gh pr list --state all` and renders compact
  open/recent-merged/closed-unmerged counts when available.
- Roadmap `Queued` rows now appear in `Current commitments` with status
  preserved.
- `open gate` is reserved for the latest session in a stream having unverified
  edits; older unverified edits render as `verification risk`.

## Open Questions

- Whether the 15-minute threshold is the right long-term cutoff for small
  but meaningful older follow-ups.
