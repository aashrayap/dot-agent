# Skills

`skills/` is the single source of truth for shared Claude and Codex skills.

The canonical repo root is `~/.dot-agent/`. Mutable outputs belong under
`~/.dot-agent/state/`, not in runtime homes or tracked repo directories.

Read `skills/AGENTS.md` before adding or materially rewriting a skill. New and
rewritten skills must include the composition contract described there.

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
- daily operating board: `~/.dot-agent/state/collab/roadmap.md`
- legacy focus compatibility file: `~/.dot-agent/state/collab/focus.md`
- compare history: `~/.dot-agent/state/collab/compare-history.md`
- thin project state: `~/.dot-agent/state/projects/<slug>/project.md`
- optional project execution memory: `~/.dot-agent/state/projects/<slug>/execution.md`
- idea incubation docs: `~/.dot-agent/state/ideas/<slug>/{idea.md,brief.md,spec.md,plan.md}`

Typical layering:

- `focus` mutates the roadmap
- `morning-sync` reads the roadmap plus active projects and proposes what should happen next
- `projects` is the thin durable bridge between roadmap rows and deep implementation
- `spec-new-feature` owns deep code-grounded planning and implementation artifacts
- `execution-review` drains completed roadmap rows and writes closure through owning helpers
