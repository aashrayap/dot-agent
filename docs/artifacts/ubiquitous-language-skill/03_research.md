---
status: complete
feature: ubiquitous-language-skill
---

# Research: ubiquitous-language-skill

## Flagged Items

- `setup.sh` should not inject language docs into arbitrary repos. Existing
  dot-agent policy says setup reports project-local instruction drift but does
  not patch project-local files.
- `/Users/ash/Documents/2026/semi-stocks` was found only as stale recent Codex
  cwd. Concrete example repo is `/Users/ash/Documents/2026/semi-stocks-2`.

## Findings

- dot-agent installs skills from `skills/<name>/skill.toml`.
- Claude receives symlinked selected entries; Codex receives copied payloads.
- Skill helpers belong in `scripts/`.
- The normal durable feature artifact owner is `spec-new-feature`, but this
  capability must be reusable outside feature planning.
- `semi-stocks-2/docs/doc-contract.md` requires repo-wide docs under `docs/`
  and forbids extra root docs beyond `README.md`, `AGENTS.md`, and `CLAUDE.md`.
- `semi-stocks-2/.codex/skills/ingest-semi/SKILL.md` proves repo-local skill
  behavior can name fixed targets and write boundaries.

## Patterns Found

- Owner-first docs.
- Setup installs runtime payloads; skill invocation mutates repo-local state.
- Progressive disclosure uses a short always-on line that points to deeper
  docs.
- Review and planning skills should consume language artifacts, not generate
  them.

## Core Docs Summary

- `AGENTS.md`: base response contract and progressive-disclosure pointers.
- `README.md`: source/install/runtime shape.
- `docs/harness-runtime-reference.md`: setup and skill packaging contract.
- `skills/AGENTS.md`: skill authoring rules.
- `skills/README.md`: composition model and workflow groups.
- `setup.sh`: installer and audit gate.

## Direction Options

- Standalone skill: chosen.
- Fold into `spec-new-feature`: rejected because too narrow.
- Fold into `review`: rejected because generation is not review ownership.
- Fold into `improve-agents-md`: rejected because language includes domain
  docs and code concepts, not only instruction files.

## Open Questions

- Whether future versions should also patch `CLAUDE.md` when present.
- Whether future versions should add setup-level report-only language drift
  audits for configured active repos.
