# Skills

`skills/` is the single source of truth for shared Claude and Codex skills.

The canonical repo root is `~/.dot-agent/`. Mutable outputs belong under
`~/.dot-agent/state/`, not in runtime homes or tracked repo directories.

## Layout

Portable skills can keep a single root `SKILL.md`:

```text
skills/explain/
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
- focus control plane: `~/.dot-agent/state/collab/focus.md`
- compare history: `~/.dot-agent/state/collab/compare-history.md`
- project state: `~/.dot-agent/state/projects/<slug>/{project.md,execution.md,AUDIT_LOG.md}`
- idea incubation docs: `~/.dot-agent/state/ideas/<slug>/{idea.md,brief.md}`

Typical layering:

- `focus` owns the lightweight day-level control plane
- `morning-sync` reads focus plus active projects and proposes what should happen next
- `projects` owns durable planning and execution memory
