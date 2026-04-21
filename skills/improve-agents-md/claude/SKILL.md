---
name: improve-agents-md
description: Improve, create, or translate agent instruction markdown such as AGENTS.md and CLAUDE.md from Claude.
---

# Improve Agent Instructions From Claude

## Composes With

- Parent: user request to create, improve, or translate agent instruction files.
- Children: none.
- Uses format from: root `improve-agents-md` workflow.
- Reads state from: repo docs, scripts, manifests, existing AGENTS.md/CLAUDE.md, and verification commands.
- Writes through: target instruction markdown files only.
- Hands off to: none.
- Receives back from: none.

Use the shared `improve-agents-md` workflow from Claude. The root skill is the
source of truth; this entrypoint only adds Claude-facing runtime bias.

Prefer improving an existing `CLAUDE.md` in place. If no useful file exists,
create one with foundational guidance visible and narrow
`<important if="...">` blocks for task-specific instructions.

When improving or translating Codex-facing files, keep Claude XML out of
`AGENTS.md`; translate conditional guidance into plain Markdown headings and
"Read When Needed" links.

Follow the shared composition and mode contract from the root skill:

- improve existing `AGENTS.md` or `CLAUDE.md` in place
- create fresh instructions when existing files are absent or obsolete
- translate paired runtime files while keeping facts aligned
- read `references/progressive-disclosure.md` for substantial rewrites
