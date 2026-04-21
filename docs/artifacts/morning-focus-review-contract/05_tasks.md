---
status: completed
feature: morning-focus-review-contract
---

# Tasks: Morning Focus Review Contract

## Execution Order

1. Update skill contracts around the new composition boundary.
2. Add a lightweight recent-work summarizer that reuses execution-review adapters/state.
3. Add recent PR discovery/verification at high-level depth.
4. Update morning-sync output format and decision prompts.
5. Add optional working-doc creation path after selected-stream approval.
6. Run setup/audit so installed Codex payloads do not drift.
7. Smoke-test morning output against a recent window without mutating roadmap.

## Task List

| ID | Task | Files | Acceptance | Verify |
|---|---|---|---|---|
| T1 | Update `morning-sync` contract | `skills/morning-sync/SKILL.md` | Composes with `execution-review` evidence intake; output order starts with recent work; `User Decides`, nested PRs, Hermes tiny status, and selected-stream prompt are documented | `rg -n "What you've been working on|User Decides|Hermes|execution-review" skills/morning-sync/SKILL.md` |
| T2 | Clarify execution-review handoff | `skills/execution-review/SKILL.md` | States lightweight morning evidence can be consumed by `morning-sync`, while full forensic review remains separate | `rg -n "morning-sync|Hermes|forensic" skills/execution-review/SKILL.md` |
| T3 | Clarify focus write gate | `skills/focus/SKILL.md` | Documents selected-stream approval, roadmap writes through `roadmap.py`, and no bulk multi-project apply | `rg -n "selected|bulk|roadmap.py|morning-sync" skills/focus/SKILL.md` |
| T4 | Build recent-work summarizer | `skills/morning-sync/scripts/recent-work-summary.py` or equivalent | Produces broad workstreams, subcategories, evidence counts, last touched, state, suggested next move, and `User Decides` candidates | `python3 skills/morning-sync/scripts/recent-work-summary.py --help` and sample window run |
| T5 | Reuse execution-review evidence | `skills/execution-review/scripts/*`, new morning helper imports | Avoids duplicating Codex/Claude log parsing; uses normalized adapters/store where practical | sample helper run shows Codex + Claude rows |
| T6 | Add PR/repo high-level verifier | morning helper or focused script | Checks roadmap/history projects plus local git repos touched recently; reports nested concise PR status/diff areas | sample helper run with `--no-network` or graceful no-PR fallback if needed |
| T7 | Add working-doc approval path | likely `skills/focus/scripts/` or `state/collab/morning/` helper | Creates one approved working doc with `Goal`, `Evidence`, `Important Docs`, `Next Step`, `Gate`; does not create docs during read-only morning scan | helper dry-run/write test |
| T8 | Setup/install | `setup.sh`, installed Codex skill copies | Codex installed payloads match source changes | `./setup.sh --check-instructions` or full `./setup.sh` if skill payloads changed |
| T9 | Smoke test morning packet | local command/manual invocation | Output hides session IDs, includes recent work, `User Decides`, nested PRs, Hermes status, and no roadmap mutation | inspect output + `git diff -- ~/.dot-agent/state/collab/roadmap.md` if applicable |

## Parallel-Safe Groups

- Group A: T1, T2, T3 are contract-only edits and can run together if write scopes stay separate.
- Group B: T4 and T5 are coupled; implement together.
- Group C: T6 can run after T4 shape is clear.
- Group D: T7 can run after T3 and after the working-doc storage decision is final.
- Group E: T8 and T9 are final gates.

## Boundaries

- Do not auto-add `User Decides` workstreams to roadmap.
- Do not bulk-apply focus changes across multiple projects.
- Do not expose session IDs or raw transcript anchors in normal morning output.
- Do not turn Hermes into source-of-truth telemetry.
- Do not create working docs unless Ash approves carrying a focus stream forward.

## Open Implementation Decisions

- Resolved: approved working documents live under `state/collab/morning/YYYY-MM-DD.md`.
- Resolved: PR verification runs opportunistically and reports a concise skipped/error state when GitHub access is unavailable.
- Resolved: the morning helper is owned by `morning-sync/scripts/` and reuses execution-review adapters.

## Implementation Result

- T1 complete: `skills/morning-sync/SKILL.md` now documents recent-work intake, `User Decides`, nested PRs, Hermes status, and selected-stream prompt.
- T2 complete: `skills/execution-review/SKILL.md` now documents the lightweight `morning-sync` intake boundary.
- T3 complete: `skills/focus/SKILL.md` now documents selected-stream writes and approval-only morning working docs.
- T4/T5 complete: `skills/morning-sync/scripts/recent-work-summary.py` summarizes recent Codex/Claude evidence without exposing session ids.
- T6 complete: recent PR lookup is implemented with a graceful unavailable/skipped path.
- T7 complete: `skills/focus/scripts/morning-working-doc.py` writes one approved local working doc.
- T8 complete: `./setup.sh` installed the changed skill payloads.
- T9 complete: source and installed smoke tests produced the morning packet without mutating roadmap state.
