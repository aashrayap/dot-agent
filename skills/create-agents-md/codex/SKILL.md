---
name: create-agents-md
description: Create, improve, or translate agent instruction markdown such as AGENTS.md and CLAUDE.md from Codex.
---

# Create AGENTS.md

## Composes With

- Parent: user request to create, improve, or translate agent instruction files.
- Children: none.
- Uses format from: root `create-agents-md` workflow.
- Reads state from: repo docs, scripts, manifests, existing AGENTS.md/CLAUDE.md, and verification commands.
- Writes through: target instruction markdown files only.
- Hands off to: none.
- Receives back from: none.

Use the shared `create-agents-md` workflow from Codex.

Prefer `AGENTS.md` for Codex-native targets. When improving or translating
Claude-facing files, preserve Claude-specific `<important if>` blocks only in
`CLAUDE.md`; do not introduce them into `AGENTS.md`.

Follow the shared composition and mode contract from the root skill:

- create fresh instructions when existing files are absent or obsolete
- improve existing `AGENTS.md` or `CLAUDE.md` in place
- translate paired runtime files while keeping facts aligned
