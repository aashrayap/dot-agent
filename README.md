# dot-claude

Shared Claude Code configuration: skills, settings, and hooks.

## Setup

Symlink shared skills into your project's `.claude/skills/`:

```sh
ln -s ~/.claude/skills/<skill-name> <project>/.claude/skills/<skill-name>
```

## Personal files

To keep files locally without pushing to the repo, add them under the `# Ash` (or your name) section in `.gitignore`.
