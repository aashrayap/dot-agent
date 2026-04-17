---
name: projects
description: Thin durable bridge for promoted workstreams, entered from Claude Code.
disable-model-invocation: true
---

# Projects Skill

## Composes With

- Parent: `roadmap.md` rows that outgrow the daily board.
- Children: `spec-new-feature` for code-grounded implementation slices; `excalidraw-diagram` when durable project state needs a visual map.
- Uses format from: shared `projects` workflow; `excalidraw-diagram` for human-facing workstream, dependency, or before/after maps when useful.
- Reads state from: `~/.dot-agent/state/projects/<slug>/project.md`, optional `execution.md`, optional `AUDIT_LOG.md`, and related roadmap rows.
- Writes through: `projects-setup.sh`, `complete-session.py`, and `update-execution.py` when execution memory exists.
- Hands off to: `spec-new-feature` when Current Slice needs deep planning or code grounding.
- Receives back from: `spec-new-feature` with PRs, pivots, and follow-ups; `execution-review` with forensic recommendations.

Use the shared `projects` workflow from Claude Code.

Run:

```bash
~/.claude/skills/projects/scripts/projects-setup.sh "$1"
```

Then follow the shared thin-project contract:

- `project.md` is the durable bridge from roadmap to implementation.
- `execution.md` and `AUDIT_LOG.md` are optional and should be ensured only when
  PRs, pivots, discarded work, or multi-session execution memory matter.
- Hand code-grounded slices to `/spec-new-feature`.
- Use or link a high-level diagram when a complex workstream, dependency shape,
  or before/after state would be easier for the human to review visually.
