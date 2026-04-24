This is Ash's global Claude Code entrypoint. Treat it as base runtime guidance,
then follow repository-local instructions in the active workspace.

Codex is Ash's preferred runtime right now. Keep shared harness work portable,
but bias day-to-day setup and workflow choices toward Codex unless Ash asks
otherwise.

## Response Contract

For non-trivial work, final responses use `This Session Focus`, `Result`, and
`Next Actions`.

- `This Session Focus`: first slot; 1-2 short lines for purpose and state.
- `Result`: changes, verification, open risks, links, and useful visuals.
- `Ledger`: only when multiple requests, corrections, parked items, or handoffs
  need explicit tracking.
- `Next Actions`: concrete follow-ups or concise user-direction questions.

Treat chat as the receipt unless durable roadmap, PR, docs, review, or handoff
state is needed. Before final response, map the latest user requests to done,
not done, or parked.

## Review

For reviews, lead with concrete findings and paths. Check behavioral
regressions, instruction drift, missing verification, and Claude/Codex contract
contradictions before summary.

<important if="you are changing dot-agent runtime config, setup, or install behavior">
Read `~/.dot-agent/AGENTS.md`. If layout, setup, runtime home, or packaging
facts matter, also read `~/.dot-agent/docs/harness-runtime-reference.md`.
</important>

<important if="you are creating or materially rewriting a skill">
Read `~/.dot-agent/skills/AGENTS.md`. Preserve runtime-visible
`## Composes With` in `SKILL.md` and local schema fields in `skill.toml`.
</important>

<important if="you are improving, creating, or translating AGENTS.md or CLAUDE.md files">
Use `~/.dot-agent/skills/improve-agents-md`. Keep always-on instructions short,
move task-specific detail behind narrow conditions, and keep Claude-only
`<important if>` blocks out of Codex `AGENTS.md`.
</important>
