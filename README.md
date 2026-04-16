# dot-agent

Ash's personal agent harness for Claude Code and Codex across work and personal
computers.

Clone this repo as `~/.dot-agent/` on each machine Ash uses. The repo is the
versioned source of truth for Ash's runtime defaults, skills, and local harness
shape. Runtime installs still live in `~/.claude/` and `~/.codex/`. Mutable
machine-local artifacts live under the gitignored `state/` subtree inside
`~/.dot-agent/`. `setup.sh` fails fast unless the repo lives at that canonical
path.

This is not a shared team distribution. Keep it optimized for Ash's work and
personal computer workflows.

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

After `./setup.sh`, the machine-level layout on each computer is:

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

Run the same setup command on both work and personal machines after pulling the
latest repo changes:

```bash
git -C ~/.dot-agent pull --ff-only
~/.dot-agent/setup.sh
```

## Versioned vs Local

- Track Ash's portable runtime defaults here.
- Keep project-specific instructions in the active repository, not in this repo-level baseline.
- Keep personal context, risky bypass flags, and extra machine-local permissions such as `skipDangerousModePermissionPrompt` or extra `Bash(...)` allow-rules out of tracked config.
- Keep machine-specific state under `~/.dot-agent/state/`; do not expect state to be identical across work and personal computers unless explicitly synced.
- Keep statusline behavior cheap and predictable. It should not poll git or network state.
- Update the repo explicitly: `git -C ~/.dot-agent pull --ff-only && ~/.dot-agent/setup.sh`
- Follow the skill composition contract in `skills/AGENTS.md` when creating or materially rewriting skills.

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

- daily operating board: `~/.dot-agent/state/collab/roadmap.md`
- legacy focus compatibility file: `~/.dot-agent/state/collab/focus.md`
- compare history: `~/.dot-agent/state/collab/compare-history.md`
- thin project state: `~/.dot-agent/state/projects/<slug>/project.md`
- optional project execution memory: `~/.dot-agent/state/projects/<slug>/execution.md`
- idea incubation docs: `~/.dot-agent/state/ideas/<slug>/{idea.md,brief.md,spec.md,plan.md}`

Daily operating loop:

- `/morning-sync` is the first morning call over roadmap plus active projects
- `/focus` mutates the roadmap
- `/projects` is the thin durable bridge between roadmap rows and `/spec-new-feature`

## Skill Migration Rules

- Do not hardcode `~/.claude` or `~/.codex` inside shared skill content.
- Shared mutable artifacts belong in `~/.dot-agent/state/`.
- Put runtime-specific behavior in `claude/` or `codex/` wrappers inside each skill when necessary.
- Keep shared scripts, assets, and references in the root skill folder.
- Reserve `.claude` and `.codex` for live runtime directories, not repo roots.
- See `skills/README.md` for the skill routing pattern.
