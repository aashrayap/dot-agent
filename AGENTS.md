# dot-agent Instructions

This repo is Ash's personal agent harness for Claude Code and Codex.
Codex is Ash's strongly preferred runtime right now; keep the harness portable,
but bias day-to-day workflow and setup decisions toward Codex unless the user
asks otherwise.

Use this file as always-on operating guidance. Pull deeper harness facts only
when the current task needs them.

## Human Response Contract

- For non-trivial work, final responses should use a concise human-readable
  packet: `This Session Focus`, `Result`, and one or more concrete
  `Next Actions`.
- `This Session Focus` is the first slot. Keep it to 1-2 short lines that
  remind Ash why this session started and where the work currently stands:
  first line for purpose, optional second line for current state.
- `Result` should carry the important receipt: what changed, what was verified,
  what remains open, and any useful visual or detail links. For workflow,
  architecture, planning, review, decision, or multi-artifact work, include or
  link the relevant visual inside `Result`.
- Use `Ledger` only when state could otherwise disappear: multiple user
  requests, corrections, follow-ups, parked items, or handoff-heavy work. Track
  `Captured`, `Done`, `Not Done`, and `Parked` when using it.
- `Next Actions` should include concrete next steps and, when useful, concise
  user-direction questions that can be answered by number or short phrase.
- Treat chat as the receipt; create durable artifacts only when the work must
  survive beyond chat, be linked from roadmap/PR/docs, be resumed by another
  session, or when multiple artifacts need a landing page.
- Before final response, map the latest user requests to the packet. Every
  request should be done, parked, or called out as not done.
- Keep this concise and runtime-portable.

## Review

- Review for behavioral regressions, instruction drift, missing verification,
  and contradictions between Claude and Codex surfaces.
- Lead with concrete findings and file paths when reviewing; keep summaries
  secondary.
- If a request is not completed, explicitly mark it as not done or parked in
  the final packet.

## Progressive Disclosure

Read these only when the task needs that layer:

- Harness layout, runtime install targets, setup rules, and skill packaging:
  `~/.dot-agent/docs/harness-runtime-reference.md`
- Skill authoring policy while creating or materially rewriting skills:
  `~/.dot-agent/skills/AGENTS.md`
- Skill catalog, install model, and current workflow diagrams:
  `~/.dot-agent/skills/README.md`
- Machine-local roadmap, ideas, reviews, and caches: files under
  `~/.dot-agent/state/` through their owning skills or helper scripts.
