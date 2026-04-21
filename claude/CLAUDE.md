This is Ash's global Claude Code entrypoint. Treat it as base runtime guidance,
then follow repository-local instructions in the active workspace.

Codex is Ash's strongly preferred runtime right now; keep shared harness changes
portable, but bias day-to-day workflow and setup decisions toward Codex unless
the user asks otherwise.

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

## Operating Loop

- Read the closest project instructions before changing files.
- Prefer small, reversible edits that preserve portable harness behavior.
- Use existing scripts, manifests, skills, and state helpers before inventing a
  parallel workflow.
- Verify with the narrowest command that proves the change, then report the
  gate clearly.

## Human Communication

- Keep chat as the receipt unless durable state is needed for handoff, roadmap,
  PR review, or multi-artifact work.
- In final responses, map each user request to done, not done, or parked.
- For reviews, lead with concrete findings and paths; keep summaries secondary.

<important if="you are changing dot-agent runtime config, setup, or install behavior">
Read `~/.dot-agent/AGENTS.md` first. If the task needs layout, setup, runtime
home, or packaging facts, also read
`~/.dot-agent/docs/harness-runtime-reference.md`.
</important>

<important if="you are creating or materially rewriting a skill">
Read `~/.dot-agent/skills/AGENTS.md` before editing. Preserve the skill's
`## Composes With` contract and runtime entries in `skill.toml`.
</important>

<important if="you are improving, creating, or translating AGENTS.md or CLAUDE.md files">
Use `~/.dot-agent/skills/improve-agents-md` as the owning workflow. Keep
always-on instructions short, move task-specific details behind narrow
conditions, and keep Claude-only `<important if>` blocks out of Codex
`AGENTS.md`.
</important>
