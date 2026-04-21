---
status: completed
feature: unified-workflow-morning-sync
---

# Feature Spec: unified-workflow-morning-sync

## Goal

Improve the unified day-start workflow so morning-sync produces a concise,
trustworthy control-plane summary for active roadmap work, recent execution
evidence, and recent PR signal.

## Users and Workflows

- Ash starts the day from `morning-sync` and expects one practical focus
  recommendation, not a transcript-derived inventory.
- Ash corrects the board in chat, then selected updates should flow through the
  roadmap control surface without hidden rewrites.
- Ash wants process-improvement observations captured during first use so they
  can be converted into focused harness changes.

## Acceptance Criteria

- Obsolete or low-value recent-work noise is either filtered out of the normal
  morning board or clearly demoted.
- Recent PR signal is not missed when known workstream repositories have recent
  PRs and lookup is available.
- PR reporting stays summary-level by workstream: no long per-PR list in the
  normal morning sync.
- The roadmap can carry `dot-agent` workflow improvement work as a visible
  active row.
- The first-use improvement tally remains durable and easy to resume.

## Boundaries

- Do not turn morning-sync into forensic execution review.
- Do not silently mutate roadmap rows during morning-sync.
- Do not require every recent PR to be listed in chat.
- Do not replace deeper PR review or feature planning workflows.

## Risks and Dependencies

- PR lookup may depend on GitHub credentials, network availability, and repo
  mapping from roadmap or local evidence.
- Recent-work evidence may include smoke tests, old shell sessions, or elapsed
  time artifacts that look more important than they are.
- Summary rules must avoid hiding genuinely important blockers or open PRs.
