---
name: improve-agents-md
description: Improve, create, or translate agent instruction markdown such as AGENTS.md and CLAUDE.md. Use to sharpen existing instructions first, create missing ones when needed, or keep Codex and Claude instruction files factually aligned.
argument-hint: [create|improve|translate] [path]
disable-model-invocation: true
---

# Improve Agent Instructions

## Composes With

- Parent: user request to create, improve, or translate agent instruction files.
- Children: `excalidraw-diagram` when instruction changes need a durable repo/runtime contract visual.
- Uses format from: `excalidraw-diagram` for human-facing instruction architecture or before/after diagrams when useful.
- Reads state from: repo docs, scripts, manifests, existing AGENTS.md/CLAUDE.md, and verification commands.
- Writes through: target instruction markdown files only.
- Hands off to: none.
- Receives back from: none.

Use this runtime-neutral workflow when a repository needs an existing
`AGENTS.md` or `CLAUDE.md` sharpened, a missing instruction file created, or
paired Claude/Codex instruction files translated while keeping facts aligned.

For substantial instruction rewrites, prefer a visual summary of the intended
repo/runtime contract when it will help the human reviewer see ownership,
setup, workflow, or before/after differences. Keep the Markdown instructions as
the executable contract; diagrams explain the shape.

## Core Workflow

1. Gather repo reality from current docs, code layout, scripts, manifests,
   existing instruction files, and verification commands.
2. Start from the existing instruction file when one exists; only fall back to a
   fresh create pass when there is no useful file to improve.
3. Classify content as always-on, conditional, referenced, or deleted.
4. Preserve accurate project identity, repo map, commands, paths, and
   verification expectations.
5. Keep always-on guidance focused on how the agent operates across planning,
   coding, execution, review, and human communication.
6. Keep foundational content visible; move testing, release, setup, skill
   authoring, and other narrow workflows behind "Read When Needed" links or
   runtime-native conditional sections.
7. Remove stale snippets, vague policy text, duplicated facts, and linter
   territory.

## Modes

| Mode | Use When | Default Target |
|------|----------|----------------|
| `improve` | A primary agent instruction file exists and should be rewritten in place | user path, `./CLAUDE.md`, then `./AGENTS.md` |
| `create` | No useful file exists, or current file is obsolete enough that salvaging it is wasteful | `./AGENTS.md` |
| `translate` | Claude and Codex instruction files need aligned facts with runtime-specific structure | both named files |

If the mode is omitted, infer it:

- existing target file -> `improve`
- no existing target file -> `create`
- two runtime files named -> `translate`

Bias toward `improve`: when a file exists, tighten it in place instead of
starting from a template.

## Create Mode

Use create mode only when there is no useful instruction file to salvage.
Use the template at `assets/AGENTS.template.md` as structure, not fixed
wording. For Claude-facing files, use `assets/CLAUDE.template.md` as structure,
not fixed wording.

The resulting instruction file should include:

1. short project/runtime identity
2. human communication contract
3. operating loop across planning, coding, execution, review, and handoff
4. progressive disclosure links or runtime-native conditional sections
5. explicit anti-patterns

## Improve Mode

This is the default path when the target file already exists. Patch the target
file in place unless the user explicitly asks for a draft in chat.

Target selection order:

1. user-provided path
2. `./CLAUDE.md`
3. `./AGENTS.md`
4. `~/.claude/CLAUDE.md`
5. `~/.codex/AGENTS.md`

If both repo-local files exist and the user did not name a target, prefer the
file for the current runtime. Ask one short question only if the target remains
ambiguous.

## Runtime Formats

For `AGENTS.md`, do not use Claude XML. Use a short always-on core, a "Read When
Needed" section, and headed conditional sections such as Planning,
Implementation, Testing, Review, Release, Setup, or Skill Authoring.

For `CLAUDE.md`, use Claude-native conditional weighting with narrow
`<important if="...">` blocks where it helps relevance. Do not wrap project
identity, directory structure, tech stack, or the human response contract if
they apply to almost every task.

For both runtimes, prefer restructuring over accretion: pull narrow workflows
out of the always-on core before adding new rules.

Read `references/progressive-disclosure.md` for substantial rewrites, paired
Claude/Codex translation, or any long file where task-specific detail is
crowding out core operating guidance.

When translating across runtimes:

- keep facts, commands, and repo paths aligned
- translate structure, not wording
- use `<important if>` only in Claude-facing files
- use headed conditional sections in Codex-facing files

## Final Checks

- Verify referenced commands and paths still exist.
- Remove contradictory runtime-specific instructions.
- Keep the always-on core short and visible.
- Make sure conditions are narrow and actionable.
- Preserve required composition information for skills.
- Compare the human response contract across `AGENTS.md`, `CLAUDE.md`, and
  human-facing companion docs such as `skills/README.md` when touched.
- Make sure the file got shorter or sharper, not broader.
