#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-work}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_SRC="$REPO_ROOT/.claude"
CODEX_SRC="$REPO_ROOT/.codex"
CLAUDE_DST="$HOME/.claude"
CODEX_DST="$HOME/.codex"
BACKUP_ROOT="$HOME/Documents/2026/dot-agent-backups/$(date +%Y%m%d%H%M%S)"

mkdir -p "$CLAUDE_DST" "$CODEX_DST" "$CODEX_DST/skills"
mkdir -p "$CLAUDE_DST/skills"

backup_and_link() {
  local src="$1"
  local dst="$2"
  local rel="$3"

  if [[ -L "$dst" ]]; then
    local current
    current="$(readlink "$dst")"
    if [[ "$current" == "$src" ]]; then
      return
    fi
  fi

  if [[ -e "$dst" || -L "$dst" ]]; then
    mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"
    mv "$dst" "$BACKUP_ROOT/$rel"
  fi

  mkdir -p "$(dirname "$dst")"
  ln -s "$src" "$dst"
}

backup_optional_dir() {
  local path="$1"
  local rel="$2"
  if [[ -d "$path" ]]; then
    mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"
    mv "$path" "$BACKUP_ROOT/$rel"
  fi
}

backup_optional_file() {
  local path="$1"
  local rel="$2"
  if [[ -e "$path" || -L "$path" ]]; then
    mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"
    mv "$path" "$BACKUP_ROOT/$rel"
  fi
}

# Claude shared payload
backup_and_link "$CLAUDE_SRC/CLAUDE.md" "$CLAUDE_DST/CLAUDE.md" ".claude/CLAUDE.md"
backup_and_link "$CLAUDE_SRC/README.md" "$CLAUDE_DST/README.md" ".claude/README.md"
backup_and_link "$CLAUDE_SRC/settings.json" "$CLAUDE_DST/settings.json" ".claude/settings.json"
backup_and_link "$CLAUDE_SRC/statusline-enhanced.sh" "$CLAUDE_DST/statusline-enhanced.sh" ".claude/statusline-enhanced.sh"
backup_and_link "$CLAUDE_SRC/collab" "$CLAUDE_DST/collab" ".claude/collab"

for skill in audit cmux compare compare-skills feature-interview idea improve-claude-md projects qa remove-slop review ship spec-new-feature wiki; do
  backup_and_link "$CLAUDE_SRC/skills/$skill" "$CLAUDE_DST/skills/$skill" ".claude/skills/$skill"
done

# Codex shared payload
backup_and_link "$CODEX_SRC/AGENTS.md" "$CODEX_DST/AGENTS.md" ".codex/AGENTS.md"
backup_and_link "$CODEX_SRC/rules" "$CODEX_DST/rules" ".codex/rules"
backup_and_link "$CODEX_SRC/config.shared.toml" "$CODEX_DST/config.shared.toml" ".codex/config.shared.toml"
backup_and_link "$CODEX_SRC/config.work.toml" "$CODEX_DST/config.work.toml" ".codex/config.work.toml"
backup_and_link "$CODEX_SRC/config.personal.toml" "$CODEX_DST/config.personal.toml" ".codex/config.personal.toml"
backup_and_link "$CODEX_SRC/install.sh" "$CODEX_DST/install.sh" ".codex/install.sh"

for skill in create-agents-md create-pr dvn-web-libraries review spec-new-feature; do
  backup_and_link "$CODEX_SRC/skills/$skill" "$CODEX_DST/skills/$skill" ".codex/skills/$skill"
done

# Remove live git metadata from runtime dirs after backup.
backup_optional_dir "$CLAUDE_DST/.git" ".claude/.git"
backup_optional_dir "$CODEX_DST/.git" ".codex/.git"

# Remove stale machine-local files that would shadow shared symlinks if present.
backup_optional_file "$CLAUDE_DST/settings.json.bak.20260407140205" ".claude/settings.json.bak.20260407140205"

"$CODEX_DST/install.sh" "$PROFILE"

echo "Linked shared .claude and .codex payloads from $REPO_ROOT"
echo "Backups stored in $BACKUP_ROOT"
