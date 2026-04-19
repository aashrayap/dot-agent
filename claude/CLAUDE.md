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

Read `~/.dot-agent/AGENTS.md` for dot-agent runtime instructions.
