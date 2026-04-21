---
status: implemented
feature: unified-workflow-morning-sync
---

# Design: unified-workflow-morning-sync

## Relevant Principles

- Keep `roadmap.md` central. Recent work and PRs explain context; they do not
  rewrite the board.
- Prefer summary over inventory. Morning output should tell Ash what deserves
  attention, not list every detected artifact.
- Separate absence from unavailability. "No PRs" means lookup succeeded and
  found none; skipped or failed lookup gets its own state.
- Keep helper output deterministic and connector fallback explicit. Scripts can
  use `gh`; Codex desktop can optionally add GitHub connector summaries.
- Demote low-value old evidence before it reaches `User Decides`.

## Decisions

### D1. Stop requiring `--skip-prs` in the normal morning-sync contract

Change `morning-sync/SKILL.md` so the default helper invocation does not pass
`--skip-prs`. Keep `--skip-prs` as an explicit offline/fast-path option.

Rationale: the skill currently says PR status is useful, but its required input
disables it.

Affected areas:
- `skills/morning-sync/SKILL.md`

Risk: local `gh` can fail. D2 handles this with explicit status text.

### D2. Replace PR listing with per-workstream PR signal summaries

Extend the helper payload/rendering to summarize PR signal as:

- `open`: count plus one attention line when nonzero
- `recent_merged`: count in recent sample/window
- `closed_unmerged`: count when present
- `source`: `gh`, `connector`, `skipped`, or `unavailable`
- `note`: short failure or skip reason

Default markdown should avoid per-PR bullet lists. It may name one open PR only
when action is needed.

Affected areas:
- `skills/morning-sync/scripts/recent-work-summary.py`
- `skills/morning-sync/SKILL.md`

Risk: `gh pr list --state all` provides a recent sample, not a complete PR
history. That is acceptable for morning signal, but not for audit.

### D3. Add structured PR lookup states

Represent these states distinctly:

- `skipped`: lookup deliberately disabled
- `unavailable`: tool/auth/network/repo error
- `empty`: lookup succeeded and found no matching PRs
- `present`: lookup succeeded and found PR signal
- `external`: assistant-side connector supplied signal

Rationale: current output collapses skipped, unavailable, and empty states into
one misleading line.

Affected areas:
- `PRSummary` / payload shape in `recent-work-summary.py`
- markdown renderer
- `morning-sync/SKILL.md` wording

### D4. Add roadmap-link repo discovery

When a roadmap row `Link` resolves to a local git root or a path inside one,
attach that repo to the roadmap stream before PR lookup.

Rationale: active roadmap work should not depend on recent session cwd capture
to discover its repo.

Affected areas:
- `build_workstreams`
- `git_root`
- PR repo mapping code

### D5. Filter stale or disposable `User Decides` rows

Default `User Decides` should include untracked work only when at least one is
true:

- touched today or yesterday
- at least two sessions
- at least 15 minutes wall time
- label/path is explicitly referenced by roadmap or fresh user context

Always suppress obvious smoke-test labels such as `Reply with exactly ok`,
one-sentence model behavior probes, and typo/test labels unless they are
touched today and repeated.

Rationale: old one-minute alias work and smoke tests should not compete with
real focus.

Affected areas:
- `build_payload`
- `render_markdown`

Risk: aggressive filtering can hide a small but important follow-up. Mitigate
with an omitted-count note only when useful.

### D6. Treat queued roadmap rows as commitments

Render queued roadmap rows under current commitments, preserving status. Primary
focus can still prefer in-progress/review/blocked rows ahead of queued rows.

Affected areas:
- `current_commitments` construction
- recommended-focus heuristic

### D7. Reframe gate signal

Replace all-stream `open gate` with either:

- `verification risk`: any recent edit-without-verification exists
- `open gate`: latest relevant session edited without verification

Rationale: long workstreams should not look blocked because of one stale
unverified session.

Affected areas:
- `stream_state`
- `suggested_next`
- open-gates rendering

## Open Risks

- `gh` may remain unreliable in the local runtime; assistant-side GitHub
  connector behavior cannot be encoded directly in the helper script.
- Recent merged PR lookup can add latency if done naively across many repos.
- Filtering `User Decides` requires a conservative first pass so small but
  important work is not hidden.
- Existing installed skill payloads will need setup after source changes.

## File Map

- `skills/morning-sync/SKILL.md`: input command, PR summary contract, fallback
  wording, output examples.
- `skills/morning-sync/scripts/recent-work-summary.py`: filtering, repo mapping,
  PR lookup status, concise PR rendering, queued commitment behavior, gate
  labels.
- `docs/artifacts/unified-workflow-morning-sync/00_summary.md`: tally updates.
- `docs/artifacts/unified-workflow-morning-sync/03_research.md`: evidence.
- `docs/artifacts/unified-workflow-morning-sync/05_tasks.md`: execution plan.
