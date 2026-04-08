# dot-agent

Shared agent configuration for Claude Code and Codex.

Clone this repo as `~/.dot-agent/`. The repo is the shared, versioned source of truth. Runtime installs still live in `~/.claude/` and `~/.codex/`. Mutable skill artifacts live under the gitignored `state/` subtree inside `~/.dot-agent/`. `setup.sh` fails fast unless the repo lives at that canonical path.

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
    ├── config.toml
    ├── rules/
    └── skills/
```

## Setup

Clone the repo into the canonical local path:

```bash
git clone https://github.com/aashrayap/dot-agent.git ~/.dot-agent
cd ~/.dot-agent
```

Then run setup:

```bash
./setup.sh
```

What `setup.sh` does:

- symlinks Claude repo config into `~/.claude/`
- symlinks Codex repo config into `~/.codex/`
- links skills into each runtime based on `skill.toml`
- creates `state/{collab,projects,ideas}`
- backs up conflicting legacy runtime files under `state/backups/setup/`

## Shared vs Local

- Track portable runtime defaults here.
- Keep project-specific instructions in the active repository, not in this repo-level baseline.
- Keep personal context, risky bypass flags, and extra machine-local permissions such as `skipDangerousModePermissionPrompt` or extra `Bash(...)` allow-rules out of tracked config.
- Keep statusline behavior cheap and predictable. It should not poll git or network state.
- Update the repo explicitly: `git -C ~/.dot-agent pull --ff-only && ~/.dot-agent/setup.sh`

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
