---
name: improve-agents-md
description: Improve, create, or translate agent instruction markdown such as AGENTS.md and CLAUDE.md from Codex.
---

# Improve Agent Instructions From Codex

## Composes With

- Parent: user request to create, improve, or translate agent instruction files.
- Children: none.
- Uses format from: root `improve-agents-md` workflow.
- Reads state from: repo docs, scripts, manifests, existing AGENTS.md/CLAUDE.md, and verification commands.
- Writes through: target instruction markdown files only.
- Hands off to: none.
- Receives back from: none.

Use the shared `improve-agents-md` workflow from Codex. The root skill is the
source of truth; this entrypoint only adds Codex-facing runtime bias.

Prefer improving an existing `AGENTS.md` in place. If no useful file exists,
create one with plain Markdown: short always-on operating guidance, "Read When
Needed" links, and headed conditional sections.

When improving or translating Claude-facing files, preserve Claude-specific
`<important if>` blocks only in `CLAUDE.md`; do not introduce them into
`AGENTS.md`.

Follow the shared composition and mode contract from the root skill:

- improve existing `AGENTS.md` or `CLAUDE.md` in place
- create fresh instructions when existing files are absent or obsolete
- translate paired runtime files while keeping facts aligned
- read `references/progressive-disclosure.md` for substantial rewrites
