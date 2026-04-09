---
name: ingest-semi
description: "Ingest, query, or lint the semi-stocks wiki at /Users/ash/Documents/2026/semi-stocks/wiki without falling back to the parent 2026 wiki."
argument-hint: "[source-or-task]"
disable-model-invocation: true
---

Use this skill when the task should operate on the semi-stocks wiki and must not touch `/Users/ash/Documents/2026/wiki`.

## Fixed targets

- Wiki root: `/Users/ash/Documents/2026/semi-stocks/wiki`
- Schema: `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md`
- Raw sources: `/Users/ash/Documents/2026/semi-stocks/wiki/raw`
- Rebuild command: `python3 ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks/wiki`

## Workflow

1. Read `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md` before doing anything else.
2. Treat `/Users/ash/Documents/2026/semi-stocks/wiki` as the only wiki root for this skill. Do not use generic wiki discovery and do not write to `/Users/ash/Documents/2026/wiki`.
3. If `$ARGUMENTS` is empty, inspect `/Users/ash/Documents/2026/semi-stocks/wiki/raw` for recently modified sources and suggest the best candidates.
4. If `$ARGUMENTS` names a file or folder without an absolute path, resolve it relative to `/Users/ash/Documents/2026/semi-stocks/wiki/raw` first.
5. Follow the ingest, query, or lint workflow from the semi-stocks schema rather than the generic wiki defaults when they differ.

## Ingest rules

- Never modify anything under `raw/`.
- Prefer updating existing pages in `sources/` and `concepts/` over creating duplicates.
- Preserve semi-stocks-specific sections such as `## Forward Claims`, `## Thesis Signal`, and `## Semi-stocks data` when they apply.
- When a source changes the thesis, bottleneck state, or tracked company signals, propose the corresponding `data/` patch explicitly.

## After every write

1. Update `/Users/ash/Documents/2026/semi-stocks/wiki/index.md`.
2. Run `python3 ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks/wiki`.
3. Append the operation to `/Users/ash/Documents/2026/semi-stocks/wiki/log.md`.

ARGUMENTS: $ARGUMENTS
