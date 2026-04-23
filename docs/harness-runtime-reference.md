# dot-agent Harness Runtime Reference

Read this only when changing harness setup, runtime config installation, skill
packaging, repo layout, or migration-sensitive behavior.

## Runtime Context

- Treat root `AGENTS.md` as base runtime context, not project-specific context.
- Follow repository-local instructions in the active workspace when present.
- Keep private context, machine-local paths, risky permission bypasses, and
  one-off local overrides out of tracked config.
- Prefer changes that preserve durable judgment, domain knowledge, evals,
  decision loops, and reusable workflow leverage.
- Keep tactical harness work migration-ready; avoid over-investing in
  tool-specific tricks likely to be replaced by a runtime release.

## Repo Shape

- `claude/` and `codex/` hold repo-side runtime config installed by `setup.sh`.
- `skills/` is the source of truth for shared skills.
- `state/` is gitignored machine-local state for roadmap, projects, ideas,
  reviews, and tool caches.
- Runtime homes are install targets, not sources of truth: `~/.claude/` and
  `~/.codex/`.

## Setup Contract

- Clone this repo at `~/.dot-agent/`.
- Run `~/.dot-agent/setup.sh` after pulling or changing skills/config.
- Do not manually copy tracked skill/config files into runtime homes except
  when debugging setup.
- Keep project-specific instructions in the active project repo, not in this
  baseline harness.

## Skill Contract

- When creating or materially rewriting a skill, follow `skills/AGENTS.md`.
- Every retained skill needs a strict `## Composes With` section.
- Use `skill.toml` to declare runtime targets, entrypoints, and local schema v1
  composition/contract fields.
- Keep shared skill behavior at the skill root; use thin runtime wrappers only
  when needed.
- Put deterministic helpers in `scripts/`, lookup docs in `references/`,
  output templates in `assets/`, and runtime-neutral support in `shared/`.

## Deterministic Checks

- `./setup.sh --check-instructions`: installed skill and repo instruction drift.
- `python3 scripts/validate-skill-manifests.py`: local skill manifest schema,
  entrypoint, composition, and dependency-path validation.
- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --format text`:
  root/skill word counts, duplicate anchors, runtime surface shape, and schema
  coverage without transcript content.
