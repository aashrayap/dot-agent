---
status: completed
feature: unified-workflow-morning-sync
---

# Tasks: unified-workflow-morning-sync

## Execution Order

1. Update morning-sync contract wording so PR lookup is not skipped by default
   and PR output is summary-level.
2. Update recent-work helper data model for PR lookup states and workstream PR
   summaries.
3. Add roadmap-link repo discovery.
4. Add `User Decides` filtering for stale/disposable evidence.
5. Fix queued-row commitment rendering and gate labels.
6. Smoke-test helper in markdown/json with and without PR lookup.
7. Run setup/audit path for changed skills.

## Task List

| ID | Task | Files | Acceptance | Verify |
|---|---|---|---|---|
| T1 | Remove default PR skip from skill contract | `skills/morning-sync/SKILL.md` | Inputs name normal helper run without `--skip-prs`; `--skip-prs` described only as fallback/offline option | `rg -n "skip-prs|Recent PRs|summary" skills/morning-sync/SKILL.md` |
| T2 | Add PR lookup state model | `skills/morning-sync/scripts/recent-work-summary.py` | Payload distinguishes skipped, unavailable, empty, present, and external/source-note states | `skills/morning-sync/scripts/recent-work-summary.py --format json --skip-prs` |
| T3 | Render concise PR summaries | `skills/morning-sync/scripts/recent-work-summary.py` | Markdown shows per-workstream PR signal summary, not a list of every PR | helper markdown smoke run |
| T4 | Discover repos from roadmap links | `skills/morning-sync/scripts/recent-work-summary.py` | Roadmap local links that resolve inside git repos add those repos to the stream PR lookup set | json smoke confirms `semi-stocks-2` and `dot-agent` repo mapping |
| T5 | Filter stale/disposable User Decides rows | `skills/morning-sync/scripts/recent-work-summary.py` | Old one-session alias/smoke rows disappear from normal `User Decides`; today/non-trivial rows remain | helper markdown smoke run against current evidence |
| T6 | Include queued roadmap commitments | `skills/morning-sync/scripts/recent-work-summary.py` | `semi-stocks-2` queued row appears as a commitment with status preserved | helper markdown smoke run |
| T7 | Refine gate labels | `skills/morning-sync/scripts/recent-work-summary.py` | stale edit-without-verification sessions produce `verification risk`; latest unverified edits produce `open gate` | focused unit-ish helper run or current evidence smoke |
| T8 | Update tally | `docs/artifacts/unified-workflow-morning-sync/00_summary.md` | Captured items marked implemented or revised after code changes | `sed -n '1,120p' docs/artifacts/unified-workflow-morning-sync/00_summary.md` |
| T9 | Setup/install | `setup.sh`, installed skill copies | Runtime skill payloads match source changes | `./setup.sh` |

## Parallel-Safe Groups

- T1 and T8 are doc-only and can run alongside helper edits.
- T2, T3, and T4 are coupled PR-helper work.
- T5, T6, and T7 touch helper classification/rendering and should be done in
  one local pass to avoid contradictory output.
- T9 runs after all source edits.

## Boundaries

- Do not add a tracked private repo map.
- Do not list every recent PR in morning output.
- Do not mutate roadmap from morning-sync.
- Do not expose raw session IDs or execution-review internals.
- Do not implement deeper PR review; summarize signal only.

## Verification Commands

```bash
python3 -m py_compile skills/morning-sync/scripts/recent-work-summary.py
skills/morning-sync/scripts/recent-work-summary.py --format json --skip-prs
skills/morning-sync/scripts/recent-work-summary.py --format markdown --skip-prs
skills/morning-sync/scripts/recent-work-summary.py --format json
git diff --check
./setup.sh
```

## Execution Checkpoint

Execution completed in `codex/unified-morning-signal-quality`.

## Implementation Result

- T1 complete: normal morning-sync input no longer requires `--skip-prs`.
- T2/T3 complete: helper emits structured PR signal states and concise
  workstream summaries.
- T4 complete: roadmap links that resolve to git repos seed PR lookup for
  roadmap streams.
- T5 complete: stale/smoke untracked work is omitted from normal output.
- T6 complete: queued roadmap rows appear in current commitments.
- T7 complete: stale unverified edits now render as `verification risk`;
  `open gate` means the latest session is unverified.
- T8 complete: this artifact set and tally were updated.
