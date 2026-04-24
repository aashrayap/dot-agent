---
status: complete
feature: ubiquitous-language-skill
---

# Tasks: ubiquitous-language-skill

## Execution Order

1. Add the standalone skill and helper.
2. Add dot-agent's own `docs/UBIQUITOUS_LANGUAGE.md` and `AGENTS.md` pointer.
3. Wire consuming skills (`spec-new-feature`, `review`).
4. Update skill catalog docs.
5. Verify setup install and helper behavior.
6. Dry-run against `/Users/ash/Documents/2026/semi-stocks-2`.
7. Ask before write-mode semi-stocks injection, commit, push, and PR.

## Task List

| ID | Task | Files | Acceptance | Verify |
|----|------|-------|------------|--------|
| T1 | Create skill shell | `skills/ubiquitous-language/SKILL.md`, `skills/ubiquitous-language/skill.toml` | Skill has strict `## Composes With`, targets Claude/Codex, and names repo artifact contract | `find skills/ubiquitous-language -maxdepth 2 -type f -print` |
| T2 | Add deterministic helper | `skills/ubiquitous-language/scripts/ubiquitous-language.py` | Supports `locate`, `init`, `inventory`, `lint`; defaults to `docs/UBIQUITOUS_LANGUAGE.md`; never patches repos without `--write` | `python3 skills/ubiquitous-language/scripts/ubiquitous-language.py --help` |
| T3 | Add dot-agent language doc | `docs/UBIQUITOUS_LANGUAGE.md` | Defines dot-agent harness terms, aliases, avoid terms, and evidence paths | `rg -n "harness|skill|roadmap|feature artifact|write-through" docs/UBIQUITOUS_LANGUAGE.md` |
| T4 | Add progressive disclosure pointer | `AGENTS.md` | One concise line points to `docs/UBIQUITOUS_LANGUAGE.md` only when shared terminology matters | `rg -n "UBIQUITOUS_LANGUAGE|Shared language" AGENTS.md` |
| T5 | Wire feature planning consumer | `skills/spec-new-feature/SKILL.md`, runtime wrappers if needed | Skill checks for language doc before `01_spec.md` and uses it for terminology alignment | `rg -n "UBIQUITOUS_LANGUAGE|ubiquitous language" skills/spec-new-feature` |
| T6 | Wire review consumer | `skills/review/SKILL.md`, `skills/review/codex/SKILL.md` if needed | Review checks terminology drift for docs/instructions/architecture/domain changes | `rg -n "terminology|UBIQUITOUS_LANGUAGE|ubiquitous language" skills/review` |
| T7 | Update skill catalog | `skills/README.md` | Catalog lists `ubiquitous-language` as a reusable support skill and explains consumers | `rg -n "ubiquitous-language|UBIQUITOUS_LANGUAGE" skills/README.md` |
| T8 | Verify install | setup/runtime payloads | `setup.sh` installs the skill; no custom repo injection added to setup | `./setup.sh --check-instructions`; `./setup.sh` |
| T9 | Dot-agent helper smoke | dot-agent repo | `locate`, `inventory`, and `lint` work in dot-agent worktree | helper commands from repo root |
| T10 | Semi-stocks dry run | `/Users/ash/Documents/2026/semi-stocks-2` | Helper identifies `/Users/ash/Documents/2026/semi-stocks-2/docs/UBIQUITOUS_LANGUAGE.md` and `AGENTS.md` pointer need without writing | helper `locate`/`inventory`/`init` without `--write` |
| T11 | Optional semi-stocks write | `/Users/ash/Documents/2026/semi-stocks-2/docs/UBIQUITOUS_LANGUAGE.md`, `AGENTS.md` | Only after explicit approval, write example artifact and AGENTS pointer | run helper with `--write`, inspect diff in semi-stocks repo |
| T12 | Commit, push, PR | dot-agent branch | Only after explicit approval; PR describes design, skill, integrations, and verification | `git status`; `git diff`; commit; push; create PR |

## Execution Notes

- T1-T10 complete in dot-agent.
- T11 intentionally not executed; semi-stocks was dry-run only per user scope.
- T12 in progress after implementation verification.

## Boundaries

- Do not edit `/Users/ash/Documents/2026/semi-stocks-2` in write mode until Ash
  explicitly approves.
- Do not add automatic language audits to `setup.sh`.
- Do not create root `UBIQUITOUS_LANGUAGE.md`.
- Do not implement a heavy semantic extractor in first wave.
- Do not stage or commit unrelated dirty files.

## Permission Gate

Before execution, ask Ash to approve:

1. Implement dot-agent skill and integrations.
2. Run write-mode example injection in `semi-stocks-2`.
3. Commit, push, and create PR.
