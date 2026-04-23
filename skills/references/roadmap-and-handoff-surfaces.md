# Roadmap And Handoff Surfaces

Use this reference when a skill needs the shared ownership map for roadmap,
idea, feature, review, and handoff state.

## Ownership

| Surface | Owner |
| --- | --- |
| `state/collab/roadmap.md` | `focus` |
| `state/ideas/<slug>/` | `idea` |
| `docs/artifacts/<feature>/` | `spec-new-feature` |
| `state/collab/daily-reviews/` | `daily-review` |
| forensic session reports/history | `execution-review` |
| `AGENTS.md` / `CLAUDE.md` creation or improvement | `improve-agents-md` |
| external remote-review packets | `handoff-research-pro` |

## Rules

- Mutate another surface only through the owning skill, helper script, or
  documented write path.
- Put delivery reality in roadmap rows, feature artifacts, PRs, daily reviews,
  or explicit handoff docs.
- Keep session IDs, dependency graph labels, and transcript anchors out of the
  human daily board unless a forensic skill explicitly owns the output.
- Use diagrams for workflow or architecture state when they help the human
  review the shape; avoid forcing diagrams into small mechanical edits.
