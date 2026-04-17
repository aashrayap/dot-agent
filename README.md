# dot-agent

Ash's personal agent harness for Claude Code and Codex.

![dot-agent runtime architecture](docs/diagrams/dot-agent-runtime-architecture.png)

`~/.dot-agent/` is the versioned source of truth. Runtime homes are install
targets. Machine-local state stays under the gitignored `state/` tree.

## Architecture

```text
~/.dot-agent/
├── AGENTS.md        # repo/group-level harness instructions
├── claude/          # Claude runtime config source and pointer file
├── codex/           # Codex config/rules source
├── skills/          # shared skill source of truth
├── state/           # gitignored local state and tool caches
├── docs/            # tracked harness docs and diagrams
├── setup.sh
└── README.md
```

Installed runtime shape:

```text
~/.claude/
├── CLAUDE.md
├── settings.json
├── statusline-enhanced.sh
└── skills/

~/.codex/
├── AGENTS.md
├── config.toml
├── rules/
└── skills/
```

## Setup

Clone at the canonical path and run setup:

```bash
git clone https://github.com/aashrayap/dot-agent.git ~/.dot-agent
~/.dot-agent/setup.sh
```

After pulling or changing skills/config:

```bash
git -C ~/.dot-agent pull --ff-only
~/.dot-agent/setup.sh
```

`setup.sh`:

- symlinks Claude config into `~/.claude/`
- symlinks root `AGENTS.md` into `~/.codex/AGENTS.md`
- symlinks Codex config/rules into `~/.codex/`
- installs skills into both runtimes based on `skill.toml`
- creates `state/{collab,projects,ideas}`
- backs up conflicting legacy runtime files under `state/backups/setup/`

## Versioned Vs Local

Track portable runtime defaults here. Keep these out of tracked config:

- private context
- machine-local trusted project paths
- risky permission bypass flags
- one-off local commands or allow rules
- generated state and tool caches

Use `state/` for local operating memory:

- `state/collab/roadmap.md`
- `state/projects/<slug>/project.md`
- `state/projects/<slug>/execution.md`
- `state/ideas/<slug>/`
- `state/tools/`

## Operating Loop

- `morning-sync` reads the day board and active projects.
- `focus` mutates the day board.
- `projects` preserves durable workstream state.
- `spec-new-feature` owns deep code-grounded planning and execution artifacts.
- `execution-review` reconciles closure and writes back through owning helpers.

## Skills

Skills live under `skills/` and install through `setup.sh`. Use
`skills/AGENTS.md` for the strict agent-facing authoring contract, and
`skills/README.md` for the human-facing skill architecture, setup, and
composability guide.
