---
status: approved
feature: skills-readme-current-state-diagram
---

# Tasks: skills-readme-current-state-diagram

## Execution Order

1. T01 — Generate new current-state Excalidraw diagram.
2. T02 — Render and inspect PNG.
3. T03 — Update `skills/README.md` image reference.
4. T04 — Move Human Response Contract to the top of root/Claude instructions.
5. T05 — Run verification/e2e.
6. T06 — Commit, push, and create PR.

## Task List

| ID | Task | Files | Verify |
|----|------|-------|--------|
| T01 | Create diagram generator and source | `docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs`, `docs/diagrams/skills-current-state-workflows.excalidraw` | `node docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs` |
| T02 | Render and inspect diagram | `docs/diagrams/skills-current-state-workflows.png` | `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/skills-current-state-workflows.excalidraw docs/diagrams/skills-current-state-workflows.png` |
| T03 | Point README at new diagram | `skills/README.md` | `rg -n "skill-workflow-prune-map|skills-current-state-workflows" skills/README.md` |
| T04 | Move Human Response Contract to top | `AGENTS.md`, `claude/CLAUDE.md` | `sed -n '1,40p' AGENTS.md`; `sed -n '1,40p' claude/CLAUDE.md` |
| T05 | Run e2e/setup checks | repository | `./setup.sh`; `git diff --check` |
| T06 | Create PR | git/GitHub | branch pushed and PR URL created |

Boundaries:
- Do not edit `codex/config.toml`; it was dirty before this run.
- Do not delete old prune-map artifacts unless separately requested.

Effort: 1-2 hours.
