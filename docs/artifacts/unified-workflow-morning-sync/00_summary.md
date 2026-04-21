---
status: implemented
feature: unified-workflow-morning-sync
---

# Unified Workflow Morning Sync

## This Tally

Track first-use feedback while the unified roadmap / morning-sync / PR-review
workflow settles.

## Captured Improvements

| # | Observation | Current Impact | Candidate Fix | Status |
|---|-------------|----------------|---------------|--------|
| 1 | Recent-work output surfaced a 4-day-old light alias follow-up under `shell/harness`. | Obsolete noise competes with real day focus. | Add stronger stale/noise filtering or demote tiny old sessions below the normal morning board. | implemented |
| 2 | Recent PRs existed for `dot-agent` and `semi-stocks-2`, but morning-sync reported none because PR lookup was skipped. | Morning sync underreported review/recent-change context. | Replace unconditional skip behavior with a concise per-repo PR summary when repo mappings are known and lookup is available. | implemented |
| 3 | PR output should not list every PR in the morning board. | Too much detail for day-start triage. | Summarize by workstream: open count, recent merged count, and attention needed. | implemented |
| 4 | `dot-agent` workflow improvement work was active but not on the roadmap. | The harness work had no durable control-plane row. | Add `dot-agent` roadmap row for unified workflow signal-quality improvements. | done |
| 5 | Helper says "No open PRs found, or PR lookup skipped/unavailable" for multiple distinct states. | Skipped, unavailable, and genuinely empty PR states collapse into one misleading line. | Emit separate states: skipped by policy, lookup unavailable, attempted with errors, or no matching PRs. | implemented |
| 6 | Queued roadmap rows can disappear from `Current commitments`. | A deliberate queued commitment can look absent during morning triage. | Treat explicit roadmap rows as commitments, with status preserved. | implemented |
| 7 | Workstream `open gate` is derived from any edit-without-verification session in the whole recent window. | Long-running streams can look blocked by stale or low-value sessions. | Weight gate state by recency, roadmap relevance, and latest verified session outcome. | implemented |

## Current PR Signal

- `dot-agent`: recent merged PRs exist; no open PR found in the latest user PR sample.
- `semi-stocks-2`: one open recent PR plus multiple recent merged PRs.
- Local helper normal PR mode now summarizes mapped GitHub repos when `gh` can
  connect, and skipped/unavailable states render distinctly when it cannot.

## Next Checkpoint

- Open PR for review.
