---
name: create-agents-md
description: Create, improve, or translate agent instruction markdown such as AGENTS.md and CLAUDE.md from Claude.
---

# Create Agent Instructions From Claude

## Composes With

- Parent: user request to create, improve, or translate agent instruction files.
- Children: none.
- Uses format from: root `create-agents-md` workflow.
- Reads state from: repo docs, scripts, manifests, existing AGENTS.md/CLAUDE.md, and verification commands.
- Writes through: target instruction markdown files only.
- Hands off to: none.
- Receives back from: none.

Use the shared `create-agents-md` workflow from Claude. The root skill is the
source of truth; this entrypoint only adds Claude-facing runtime bias.

Prefer `CLAUDE.md` for Claude-native targets. Keep foundational guidance visible
and use narrow `<important if="...">` blocks for task-specific instructions.

When improving or translating Codex-facing files, keep Claude XML out of
`AGENTS.md`; translate conditional guidance into plain Markdown headings and
"Read When Needed" links.

Follow the shared composition and mode contract from the root skill:

- create fresh instructions when existing files are absent or obsolete
- improve existing `AGENTS.md` or `CLAUDE.md` in place
- translate paired runtime files while keeping facts aligned
- read `references/progressive-disclosure.md` for substantial rewrites
