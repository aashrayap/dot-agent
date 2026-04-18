---
status: complete
feature: human-review-surface-contract
---

# Tasks: human-review-surface-contract

## Execution Order

1. Establish root and skill contract surfaces.
2. Add callable Excalidraw diagram skill and durable diagrams.
3. Split human daily loop from project/session internals.
4. Split human closure from forensic execution review.
5. Promote visual-first presentation into human-facing skill contracts.
6. Harden renderer determinism and run setup/verification.

## Task List

| Task | Status | Files |
|------|--------|-------|
| Root runtime contract | Done | `AGENTS.md`, `README.md`, `claude/CLAUDE.md`, `setup.sh` |
| Skill authoring contract | Done | `skills/AGENTS.md`, `skills/README.md` |
| Excalidraw skill | Done | `skills/excalidraw-diagram/**` |
| Compare visual composition | Done | `skills/compare/SKILL.md` |
| Human daily loop contract | Done | `skills/morning-sync/SKILL.md`, `skills/focus/SKILL.md`, `skills/daily-review/**` |
| Roadmap helper schema | Done | `skills/focus/scripts/roadmap.py` |
| Execution-review forensic boundary | Done | `skills/execution-review/**` |
| Visual-first human presentation | Done | `skills/README.md`, selected human-facing `SKILL.md` files |
| Before/after diagram | Done | `docs/diagrams/human-review-surface-before-after.*` |

## Verification

- `./setup.sh`
- `python3 -m json.tool docs/diagrams/*.excalidraw`
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh`
- `git diff --check`
- spot-check installed runtime skill copies for changed skills
