# dot-agent

Shared agent configuration for Claude Code and Codex.

Clone this repo as `~/.dot-agent/`. The repo is the shared, versioned source of truth. Runtime installs still live in `~/.claude/` and `~/.codex/`. Mutable skill artifacts live under the gitignored `state/` subtree inside `~/.dot-agent/`.

## Repo Layout

```text
~/.dot-agent/
├── claude/          # repo-side Claude config
├── codex/           # repo-side Codex config
├── skills/          # single source of truth for skills
├── state/           # gitignored machine-local artifacts
│   ├── collab/
│   ├── projects/
│   └── ideas/
├── .gitignore
├── README.md
└── setup.sh
```

## Installed Layout

After `./setup.sh`, the machine-level layout is:

```text
~/
├── .dot-agent/      # this repo
├── .claude/         # Claude runtime install
│   ├── CLAUDE.md
│   ├── settings.json
│   ├── statusline-enhanced.sh
│   └── skills/
└── .codex/          # Codex runtime install
    ├── AGENTS.md
    ├── config.shared.toml
    ├── config.work.toml
    ├── config.personal.toml
    ├── config.toml
    ├── rules/
    └── skills/
```

## Setup

Run:

```bash
./setup.sh
```

Optional Codex profile:

```bash
./setup.sh personal
```

What `setup.sh` does:

- symlinks Claude repo config into `~/.claude/`
- symlinks Codex repo config into `~/.codex/`
- renders `~/.codex/config.toml` from the shared file plus the selected profile
- links skills into each runtime based on `skill.toml`
- creates `state/{collab,projects,ideas}`
- backs up conflicting legacy runtime files under `state/backups/setup/`

## Skill Layout

- Keep runtime config separate: `claude/` for Claude, `codex/` for Codex.
- Keep skills unified under `skills/`.
- Prefer shared skill content with thin runtime wrappers only where needed.
- Put runtime-specific wrappers inside the skill folder, not in separate top-level skill trees.

Example:

```text
skills/review/
├── SKILL.md
├── codex/
│   └── SKILL.md
├── scripts/
└── skill.toml
```

`skill.toml` controls which runtimes receive the skill and which entrypoint each runtime should use.

## Mutable State

Shared mutable artifacts belong under `~/.dot-agent/state/`, not in tracked source directories and not in runtime homes.

Examples:

- compare history: `~/.dot-agent/state/collab/compare-history.md`
- project state: `~/.dot-agent/state/projects/<slug>/`
- idea incubation docs: `~/.dot-agent/state/ideas/<slug>/`

## Skill Migration Rules

- Do not hardcode `~/.claude` or `~/.codex` inside shared skill content.
- Shared mutable artifacts belong in `~/.dot-agent/state/`.
- Put runtime-specific behavior in `claude/` or `codex/` wrappers inside each skill when necessary.
- Keep shared scripts, assets, and references in the root skill folder.
- Reserve `.claude` and `.codex` for live runtime directories, not repo roots.
- See `skills/README.md` for the skill routing pattern.
