---
name: create-agents-md
description: Create a fresh Codex-native AGENTS.md for a repository using current workflow expectations, repo conventions, and concise operational rules. Treat existing AGENTS.md as legacy unless the user explicitly asks to salvage it.
---

# Create AGENTS.md

Use this when a repository needs a new `AGENTS.md` for Codex, or when the current instruction file is obsolete enough that patching it is a waste of time.

## Default Target

If the user does not specify a path, write `./AGENTS.md`.

## Rules

- Do not treat an existing `AGENTS.md` as source of truth unless the user explicitly asks to salvage part of it.
- Gather repo reality from current docs, code layout, scripts, and verification commands.
- Use the template at `assets/AGENTS.template.md` as structure, not as fixed wording.
- Keep the file concise, operational, and specific to the repository.
- Prefer rules that change behavior over philosophy statements.
- Remove tool assumptions that are not actually available in Codex.
- If a convention is uncertain, ask or mark it as a deliberate placeholder instead of inventing certainty.

## Inputs to Gather

- user workflow preferences from the current conversation
- active repo conventions from README files, docs, scripts, manifests, and code patterns
- verification commands that actually work in the repo
- review and planning expectations

## Output Requirements

The resulting `AGENTS.md` should include:

1. core operating rules
2. coding conventions
3. workflow expectations
4. conditional guidance for planning, implementation, and review
5. explicit anti-patterns

## What Good Output Looks Like

- short always-on rules at the top
- conditional guidance separated cleanly
- concrete commands, file locations, and expectations where possible
- no generic filler
- no stale references to Claude-only workflows or removed skill systems

## Non-Goals

- preserving obsolete instruction text
- literal migration from a legacy instruction file
- writing a broad policy manual
