---
name: execution-review
description: Review recent Codex sessions to produce a daily or weekly workflow reflection, quantify context switching, and run a grounded execution scorecard from the local ~/.codex session store.
---

# Execution Review

Use this when the user wants a daily review, weekly review, execution reflection, Codex workflow analysis, context-switching diagnosis, or an eval/judge pass over recent Codex work.

## Quick Start

1. Run `scripts/execution-review-setup.py [window]` first.
2. Run `scripts/fetch-codex-sessions.py --window <window>` to get the full thread list and aggregate signals.
3. Inspect only the threads that matter with `scripts/inspect-codex-session.py --thread-id <id>`.

`window` accepts `day`, `week`, raw hours like `24`, or suffixed values like `36h`, `7d`.

## Intent

The scripts provide deterministic signals from `~/.codex/state_*.sqlite` and `~/.codex/sessions/**`. Your job is to turn those signals into a useful reflection loop:

- what workstreams actually consumed time
- where context switching showed up
- which sessions were deep and effective
- which sessions were shallow, repetitive, or under-validated
- what workflow changes to test next

## Workflow

### Daily Review

Use a `day` or `24` window unless the user says otherwise.

1. Run setup.
2. Run `scripts/fetch-codex-sessions.py --window <window>`.
3. From the fetched output, identify:
   - top 3 threads by `wall_seconds`
   - every thread with `apply_patches > 0` and `verification_commands == 0`
   - every thread with `exec_failures > 0`
   - one thread that looks especially strong
4. Run `scripts/inspect-codex-session.py --thread-id <id>` for that small set.
5. Cluster threads into logical workstreams. A workstream is not always a repo or cwd. Use `cwd`, `label`, `first_user_message`, and inspected evidence.
6. Produce the report.

### Weekly Review

Use a `week` or `7d` window unless the user says otherwise.

1. Run setup.
2. Run `scripts/fetch-codex-sessions.py --window <window>`.
3. Use the `days` section to spot:
   - heavy context-switch days
   - days with strong verification coverage
   - repeated failure patterns
   - under-finished days with many short threads
4. Inspect representative threads:
   - the best day
   - the worst day
   - one recurring failure case
   - one session that shows clear depth
5. Produce the weekly pattern review and 1-3 process experiments for next week.

## Judge Rules

Judge only after you have deterministic evidence. Never score from vibes alone.

Use this rubric:

| Dimension | What to look for |
| --- | --- |
| Focus | Low thread churn, coherent workstream, limited avoidable cwd switching |
| Grounding | Early repo/runtime inspection before large claims or edits |
| Depth | The session moves past surface reading into decisions, edits, or resolved conclusions |
| Verification | Tests, lint, diff checks, or another explicit validation loop after meaningful changes |
| Closure | Clear final outcome, risks, and next steps instead of a dangling stop |

Score each dimension `1-5`, then explain the score with concrete evidence from the inspected threads.

## Guardrails

- Default to top-level threads only. The fetch script excludes spawned subthreads unless explicitly told otherwise.
- Prefer a small number of inspected threads over opening everything.
- Treat `cwd` as a hint, not the truth. Work can span multiple repos.
- `wall_seconds` is session span, not human-vs-AI active time.
- A no-edit research session is not automatically bad. Judge it on whether it reduced uncertainty decisively.
- An edit session with no validation is a real risk and should be called out directly.

## Output Contract

For a daily review, produce:

```markdown
# Daily Execution Review — <date>

## Topline
- <2-4 sentence read on how the day was actually spent>

## Workstream Ribbon
| Time | Wall | Workstream | cwd(s) | Thread IDs |
| --- | --- | --- | --- | --- |

## What Went Well
- <evidence-backed point>

## What Went Poorly
- <evidence-backed point>

## Scorecard
| Dimension | Score | Why |
| --- | --- | --- |

## Tomorrow's Process Changes
1. <specific change>
2. <specific change>
3. <specific change>
```

For a weekly review, produce:

```markdown
# Weekly Execution Review — <date range>

## Week Pattern
- <2-4 sentence read>

## Day Table
| Day | Threads | Cwds | Wall | Context Switches | Apply Patches | Verification |
| --- | --- | --- | --- | --- | --- | --- |

## Repeated Strengths
- <pattern>

## Repeated Failure Modes
- <pattern>

## Scorecard
| Dimension | Score | Why |
| --- | --- | --- |

## Next Week Experiments
1. <specific experiment>
2. <specific experiment>
3. <specific experiment>
```

If the user asks to save the report, write it under `~/.dot-agent/state/collab/execution-reviews/`.
