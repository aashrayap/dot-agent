---
status: complete
feature: hermes-always-on-thesis
---

# Tasks: hermes-always-on-thesis

## Execution Order

1. Add Hermes daily producer script.
2. Update execution-review docs so agents know when Hermes findings reach human review.
3. Run producer dry-run and write-run for today.
4. Verify syntax, whitespace, generated files, and existing morning status compatibility.
5. Create background heartbeat.
6. Record completion in this artifact.

## Task List

| ID | Task | Files | Acceptance | Verify |
|---|---|---|---|---|
| H1 | Daily producer | `skills/execution-review/scripts/hermes-daily.py` | Script scopes to `dot-agent` and `semi-stocks-2`, writes thesis/log/synthesis, and emits compatibility findings only when needed | `python3 -m py_compile ...`; dry run; write run |
| H2 | Human review contract | `skills/execution-review/SKILL.md`, runtime wrappers | Docs state findings reach human review via daily synthesis, heartbeat inbox, morning tiny status, and execution-review detail | `rg -n "Hermes Daily|human review" skills/execution-review` |
| H3 | E2E generated output | `state/collab/hermes/...` | Today's thesis/log/synthesis exist and synthesis has a Human Review section | `test -s ...`; inspect synthesis |
| H4 | Background default | App heartbeat automation | Active heartbeat runs producer and opens inbox with review-worthy findings or no-new-finding status | automation card created |
| H5 | Artifact closeout | `docs/artifacts/hermes-always-on-thesis/*` | Summary/design/tasks reflect completed execution | inspect docs |

## Completion Log

- H1 complete: `skills/execution-review/scripts/hermes-daily.py` added and verified with dry-run/write-run.
- H2 complete: execution-review shared and runtime wrapper docs now describe the Hermes daily producer and human review timing.
- H3 complete: generated `state/collab/hermes/thesis.md`, `state/collab/hermes/daily/2026-04-21-log.jsonl`, and `state/collab/hermes/daily/2026-04-21.md`.
- H4 complete: created active hourly `Hermes Watch` heartbeat.
- H5 complete: feature artifacts updated with design, task, and execution receipt.
