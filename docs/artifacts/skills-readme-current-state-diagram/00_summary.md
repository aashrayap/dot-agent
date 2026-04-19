---
status: complete
feature: skills-readme-current-state-diagram
---

# Summary: skills-readme-current-state-diagram

## Result

Replaced the `skills/README.md` diagram with a current-state skills setup and
workflow map, then moved the Human Response Contract to the top of root
`AGENTS.md` and `claude/CLAUDE.md`.

## Visual

![Current skills setup and workflows](../../diagrams/skills-current-state-workflows.png)

## Artifacts

- `01_spec.md` — approved scope and acceptance criteria.
- `02_questions.md` — approved research questions.
- `03_research.md` — current setup findings.
- `04_design.md` — diagram and instruction-placement decisions.
- `05_tasks.md` — execution checklist and verification plan.

## Gate

- Rendered Excalidraw PNG.
- Ran `./setup.sh` successfully.
- Ran `git diff --cached --check` successfully before commit.
- Created PR: https://github.com/aashrayap/dot-agent/pull/29.
