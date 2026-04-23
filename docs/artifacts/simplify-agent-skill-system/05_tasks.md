---
status: completed
feature: simplify-agent-skill-system
---

# Tasks: simplify-agent-skill-system

## Execution Order

1. Done: Update human response protocol in root/template docs.
2. Done: Add `visual-reasoning` grouped skill.
3. Done: Update skill catalog and diagrams.
4. Done: Run setup/audit verification for skill install drift.

## Task List

| ID | Task | Files | Gate |
|----|------|-------|------|
| T1 | Thin human response protocol | `AGENTS.md`, `skills/create-agents-md/assets/AGENTS.template.md`, `skills/create-agents-md/assets/CLAUDE.template.md`, `skills/README.md` | `rg -n "This Session Focus|Human Response Contract|Ledger|Visual|Gate|Next Actions" ...` |
| T2 | Add grouped visual reasoning skill | `skills/visual-reasoning/SKILL.md`, `skills/visual-reasoning/skill.toml` | `find skills/visual-reasoning -maxdepth 2 -type f -print` |
| T3 | Wire visual reasoning composition | `skills/README.md`, maybe child `SKILL.md` files | `rg -n "visual-reasoning|visual reasoning" skills` |
| T4 | Update diagram if useful | `docs/diagrams/skill-composability-workflow.excalidraw`, `.png` | render command succeeds and PNG exists |
| T5 | Verify install/audit path | setup/audit commands discovered from repo | command output shows new skill installed or no drift |

## Gate Results

- `node docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs`
  regenerated the current workflow Excalidraw source.
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh
  docs/diagrams/skills-current-state-workflows.excalidraw
  docs/diagrams/skills-current-state-workflows.png` rendered the PNG.
- Visual inspection passed for the rendered workflow diagram.
- `./setup.sh` installed runtime payloads and ran audits.
- Skill Instruction Audit: checked 16 skills and 28 runtime payloads; no skill
  instruction drift found.
- Repo Instruction Audit: completed with existing downstream workspace warnings
  outside this change.
- `git diff --check` passed.

## Boundaries

- Do not delete skills.
- Do not merge `explain`, `compare`, or `excalidraw-diagram`.
- Keep `Composes With` schema unchanged.
- Keep visual-reasoning entrypoint lean; route to children instead of copying
  their full instructions.
