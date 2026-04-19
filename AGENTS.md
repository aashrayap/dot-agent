# dot-agent Instructions

## Human Response Contract

- For non-trivial work, final responses should return a concise human-readable
  packet: `This Session Focus`, `Result`, `Visual`, `Gate`, `Ledger`, one or
  more concrete `Next Actions`, and `Details` links.
- `This Session Focus` is the first slot. Keep it to 1-2 short lines that
  remind Ash why this session started and where the work currently stands:
  first line for purpose, optional second line for current state.
- `Visual` is always a slot. For workflow, architecture, planning, review,
  decision, or multi-artifact work, link an existing diagram or create/render
  one. For narrow mechanical work, say why no visual was useful.
- Use `Ledger` when the session has multiple user requests, corrections, or
  follow-ups. Track `Captured`, `Done`, `Not Done`, and `Parked` so nothing
  disappears into chat.
- Treat chat as the receipt; create durable artifacts only when the work must
  survive beyond chat, be linked from roadmap/PR/docs, be resumed by another
  session, or when multiple artifacts need a landing page.
- Before final response, map the latest user requests to the packet. Every
  request should be done, parked, or called out as not done.
- Keep this concise and runtime-portable.

This repo is Ash's personal agent harness for Claude Code and Codex.
Codex is Ash's strongly preferred runtime right now; keep the harness portable,
but bias day-to-day workflow and setup decisions toward Codex unless the user
asks otherwise.

## Runtime Context

- Treat this file as base runtime context, not project-specific context.
- Follow repository-local instructions in the active workspace when present.
- Keep private context, machine-local paths, risky permission bypasses, and one-off local overrides out of tracked config.
- Prefer changes that preserve durable judgment, domain knowledge, evals, decision loops, and reusable workflow leverage.
- Keep tactical harness work migration-ready; avoid over-investing in tool-specific tricks likely to be replaced by a runtime release.

## Repo Shape

- `claude/` and `codex/` hold repo-side runtime config installed by `setup.sh`.
- `skills/` is the source of truth for shared skills.
- `state/` is gitignored machine-local state for roadmap, projects, ideas, reviews, and tool caches.
- Runtime homes are install targets, not sources of truth: `~/.claude/` and `~/.codex/`.

## Setup Contract

- Clone this repo at `~/.dot-agent/`.
- Run `~/.dot-agent/setup.sh` after pulling or changing skills/config.
- Do not manually copy tracked skill/config files into runtime homes except when debugging setup.
- Keep project-specific instructions in the active project repo, not in this baseline harness.

## Skill Contract

- When creating or materially rewriting a skill, follow `skills/AGENTS.md`.
- Every retained skill needs a strict `## Composes With` section.
- Use `skill.toml` to declare runtime targets and entrypoints.
- Keep shared skill behavior at the skill root; use thin runtime wrappers only when needed.
- Put deterministic helpers in `scripts/`, lookup docs in `references/`, output templates in `assets/`, and runtime-neutral support in `shared/`.
