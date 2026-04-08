# Skills

`skills/` is the single source of truth for shared Claude and Codex skills.

The canonical repo root is `~/.dot-agent/`. Mutable outputs belong under
`~/.dot-agent/state/`, not in runtime homes or tracked repo directories.

## Layout

Portable skills can keep a single root `SKILL.md`:

```text
skills/remove-slop/
├── SKILL.md
└── skill.toml
```

Skills with runtime-specific entrypoints keep wrappers inside the skill folder:

```text
skills/review/
├── SKILL.md
├── codex/
│   └── SKILL.md
├── scripts/
└── skill.toml
```

Codex-only skills keep only a Codex wrapper:

```text
skills/create-agents-md/
├── codex/
│   └── SKILL.md
└── skill.toml
```

## Routing

The repo-root `setup.sh` reads `skill.toml` when present.

- `targets` decides whether a skill is linked to Claude, Codex, or both.
- `default_entry` points at a shared `SKILL.md`.
- `claude_entry` and `codex_entry` override the shared entry per runtime.

If `skill.toml` is missing, the skill defaults to Claude-only and links the root `SKILL.md`.

## Shared State

When a skill needs persistent mutable storage, write it under:

```text
~/.dot-agent/state/
├── collab/
├── projects/
└── ideas/
```

Examples:
- compare history: `~/.dot-agent/state/collab/compare-history.md`
- project state: `~/.dot-agent/state/projects/<slug>/`
- idea incubation docs: `~/.dot-agent/state/ideas/<slug>/`
