---
name: improve-agent-md
description: Legacy alias for create-agents-md improve mode. Use create-agents-md for new work.
argument-hint: [path-to-agent-md]
disable-model-invocation: true
---

# Improve Agent Markdown

## Composes With

- Parent: legacy user invocation.
- Children: `create-agents-md`.
- Uses format from: none.
- Reads state from: target instruction files.
- Writes through: `create-agents-md` improve mode.
- Hands off to: `create-agents-md`.
- Receives back from: none.

This skill is retained as a compatibility alias.

Use `create-agents-md` in improve mode for the actual workflow:

- improve existing `AGENTS.md` or `CLAUDE.md` in place
- preserve accurate commands, paths, and repo conventions
- keep Claude and Codex instruction files factually aligned when translating

Do not add new behavior here. Add future agent-instruction behavior to
`create-agents-md`.
