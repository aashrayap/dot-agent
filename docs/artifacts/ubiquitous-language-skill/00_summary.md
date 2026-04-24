---
status: complete
feature: ubiquitous-language-skill
---

# Ubiquitous Language Skill

## Decision

Build a standalone user-level dot-agent skill named `ubiquitous-language`.

It installs through `~/.dot-agent/setup.sh` like other skills, but it injects
repo-local language docs only when the skill is invoked inside a repo.

## Target Shape

- Skill source: `skills/ubiquitous-language/`
- Default repo artifact: `docs/UBIQUITOUS_LANGUAGE.md`
- Repo instruction pointer: one progressive-disclosure line in `AGENTS.md`
- Example repo: `/Users/ash/Documents/2026/semi-stocks-2`
- Main success metric: implementation alignment

## Checkpoint

Implementation is complete for dot-agent. Semi-stocks was dry-run only. Commit,
push, and PR are part of this execution wave.

## Verification

- `python3 -m py_compile skills/ubiquitous-language/scripts/ubiquitous-language.py`
- `python3 skills/ubiquitous-language/scripts/ubiquitous-language.py lint --strict`
- `python3 skills/ubiquitous-language/scripts/ubiquitous-language.py init`
- `python3 skills/ubiquitous-language/scripts/ubiquitous-language.py locate --repo /Users/ash/Documents/2026/semi-stocks-2`
- `python3 skills/ubiquitous-language/scripts/ubiquitous-language.py init --repo /Users/ash/Documents/2026/semi-stocks-2`
- temp-home `setup.sh` install check, followed by strict skill/repo audits with `uv run python`
