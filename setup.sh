#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 0 ]]; then
  echo "ERROR: setup.sh takes no arguments"
  echo "Usage: ./setup.sh"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
EXPECTED_DOT_AGENT_HOME="$HOME/.dot-agent"
COMMON_GIT_DIR="$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null || true)"
if [[ -n "$COMMON_GIT_DIR" && "$COMMON_GIT_DIR" != /* ]]; then
  COMMON_GIT_DIR="$(cd "$REPO_ROOT/$COMMON_GIT_DIR" && pwd -P)"
fi

CANONICAL_REPO_ROOT=""
if [[ -n "$COMMON_GIT_DIR" ]]; then
  CANONICAL_REPO_ROOT="$(cd "$COMMON_GIT_DIR/.." && pwd -P)"
fi

if [[ "$REPO_ROOT" != "$EXPECTED_DOT_AGENT_HOME" && "$CANONICAL_REPO_ROOT" != "$EXPECTED_DOT_AGENT_HOME" ]]; then
  echo "ERROR: dot-agent must live at $EXPECTED_DOT_AGENT_HOME"
  echo "Current repo root: $REPO_ROOT"
  echo "Clone or move the repo, then rerun setup:"
  echo "  git clone https://github.com/aashrayap/dot-agent.git $EXPECTED_DOT_AGENT_HOME"
  echo "  cd $EXPECTED_DOT_AGENT_HOME"
  echo "  ./setup.sh"
  exit 1
fi

DOT_AGENT_HOME="$EXPECTED_DOT_AGENT_HOME"
DOT_AGENT_SOURCE_ROOT="$REPO_ROOT"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
CLAUDE_SRC="$DOT_AGENT_SOURCE_ROOT/claude"
CODEX_SRC="$DOT_AGENT_SOURCE_ROOT/codex"
SKILLS_SRC="$DOT_AGENT_SOURCE_ROOT/skills"
CLAUDE_DST="$HOME/.claude"
CODEX_DST="$HOME/.codex"
BACKUP_ROOT="$DOT_AGENT_STATE_HOME/backups/setup/$(date +%Y%m%d%H%M%S)"

mkdir -p \
  "$CLAUDE_DST/skills" \
  "$CODEX_DST/skills" \
  "$DOT_AGENT_STATE_HOME/collab" \
  "$DOT_AGENT_STATE_HOME/ideas"

ensure_backup_dir() {
  mkdir -p "$BACKUP_ROOT"
}

backup_path() {
  local path="$1"
  local rel="$2"

  if [[ -e "$path" || -L "$path" ]]; then
    ensure_backup_dir
    mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"
    mv "$path" "$BACKUP_ROOT/$rel"
  fi
}

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

  backup_path "$dst" "$rel"
  mkdir -p "$(dirname "$dst")"
  ln -s "$src" "$dst"
}

copy_dir_contents() {
  local src_dir="$1"
  local dst_dir="$2"

  mkdir -p "$dst_dir"
  cp -R "$src_dir"/. "$dst_dir"
}

sync_dir_from_temp() {
  local tmp_dir="$1"
  local dst_dir="$2"
  local rel="$3"

  if [[ -d "$dst_dir" && ! -L "$dst_dir" ]] \
    && [[ -z "$(find "$dst_dir" -type l -print -quit)" ]] \
    && diff -qr "$tmp_dir" "$dst_dir" >/dev/null 2>&1; then
    rm -rf "$tmp_dir"
    return
  fi

  backup_path "$dst_dir" "$rel"
  mkdir -p "$(dirname "$dst_dir")"
  mv "$tmp_dir" "$dst_dir"
}

cleanup_legacy_path() {
  local path="$1"
  local rel="$2"

  if [[ -e "$path" || -L "$path" ]]; then
    backup_path "$path" "$rel"
  fi
}

cleanup_removed_skill() {
  local skill_name="$1"

  cleanup_legacy_path "$CLAUDE_DST/skills/$skill_name" ".claude/skills/$skill_name"
  cleanup_legacy_path "$CODEX_DST/skills/$skill_name" ".codex/skills/$skill_name"
}

read_scalar() {
  local key="$1"
  local file="$2"
  sed -n "s/^${key} = \"\\(.*\\)\"$/\\1/p" "$file"
}

read_targets() {
  local file="$1"
  sed -n 's/^targets = \[\(.*\)\]$/\1/p' "$file" \
    | tr -d ' "' \
    | tr ',' '\n'
}

has_target() {
  local runtime="$1"
  local manifest="$2"
  read_targets "$manifest" | grep -qx "$runtime"
}

link_claude_payload() {
  backup_and_link "$CLAUDE_SRC/.gitignore" "$CLAUDE_DST/.gitignore" ".claude/.gitignore"
  backup_and_link "$CLAUDE_SRC/CLAUDE.md" "$CLAUDE_DST/CLAUDE.md" ".claude/CLAUDE.md"
  backup_and_link "$CLAUDE_SRC/settings.json" "$CLAUDE_DST/settings.json" ".claude/settings.json"
  backup_and_link "$CLAUDE_SRC/statusline-enhanced.sh" "$CLAUDE_DST/statusline-enhanced.sh" ".claude/statusline-enhanced.sh"
}

ensure_codex_rules() {
  local dst_dir="$CODEX_DST/rules"
  local tmp_dir

  tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/dot-agent-codex-rules.XXXXXX")"

  for src_file in "$CODEX_SRC"/rules/*; do
    local name

    [[ -e "$src_file" ]] || continue
    name="$(basename "$src_file")"
    cp "$src_file" "$tmp_dir/$name"
  done

  sync_dir_from_temp "$tmp_dir" "$dst_dir" ".codex/rules"
}

link_codex_payload() {
  backup_and_link "$DOT_AGENT_SOURCE_ROOT/AGENTS.md" "$CODEX_DST/AGENTS.md" ".codex/AGENTS.md"
  backup_and_link "$CODEX_SRC/config.toml" "$CODEX_DST/config.toml" ".codex/config.toml"
  backup_and_link "$CODEX_SRC/hooks.json" "$CODEX_DST/hooks.json" ".codex/hooks.json"
  ensure_codex_rules
}

install_codex_skill_runtime() {
  local skill_dir="$1"
  local entry="$2"
  local dst_root="$3"
  local rel_prefix="$4"
  local source="$skill_dir/$entry"
  local source_parent
  local tmp_dir
  local dst_dir

  source_parent="$(dirname "$source")"
  tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/dot-agent-codex-skill.XXXXXX")"
  dst_dir="$dst_root/skills/$(basename "$skill_dir")"

  if [[ "$source_parent" == "$skill_dir" ]]; then
    cp "$source" "$tmp_dir/SKILL.md"
  else
    copy_dir_contents "$source_parent" "$tmp_dir"
    if [[ ! -f "$tmp_dir/SKILL.md" ]]; then
      echo "WARN: Codex skill payload for $(basename "$skill_dir") did not produce SKILL.md"
      rm -rf "$tmp_dir"
      return
    fi
  fi

  for shared_dir in scripts assets references shared; do
    if [[ -e "$skill_dir/$shared_dir" ]]; then
      copy_dir_contents "$skill_dir/$shared_dir" "$tmp_dir/$shared_dir"
    fi
  done

  sync_dir_from_temp "$tmp_dir" "$dst_dir" "$rel_prefix"
}

link_skill_runtime() {
  local runtime="$1"
  local dst_root="$2"
  local skill_dir="$3"
  local skill_name
  local manifest
  local rel_prefix
  local entry=""
  local source=""

  skill_name="$(basename "$skill_dir")"
  manifest="$skill_dir/skill.toml"
  rel_prefix=".${runtime}/skills/$skill_name"

  if [[ -f "$manifest" ]]; then
    if ! has_target "$runtime" "$manifest"; then
      return
    fi

    entry="$(read_scalar "${runtime}_entry" "$manifest")"
    if [[ -z "$entry" ]]; then
      entry="$(read_scalar "default_entry" "$manifest")"
    fi
  else
    if [[ "$runtime" != "claude" || ! -f "$skill_dir/SKILL.md" ]]; then
      return
    fi
    entry="SKILL.md"
  fi

  if [[ -z "$entry" ]]; then
    echo "WARN: No ${runtime} entry for skill $skill_name"
    return
  fi

  source="$skill_dir/$entry"
  if [[ ! -f "$source" ]]; then
    echo "WARN: Missing ${runtime} skill entry for $skill_name: $source"
    return
  fi

  if [[ "$runtime" == "codex" ]]; then
    install_codex_skill_runtime "$skill_dir" "$entry" "$dst_root" "$rel_prefix"
    return
  fi

  backup_and_link "$source" "$dst_root/skills/$skill_name/SKILL.md" "$rel_prefix/SKILL.md"

  for shared_dir in scripts assets references shared; do
    if [[ -e "$skill_dir/$shared_dir" ]]; then
      backup_and_link \
        "$skill_dir/$shared_dir" \
        "$dst_root/skills/$skill_name/$shared_dir" \
        "$rel_prefix/$shared_dir"
    fi
  done
}

link_skills() {
  local skill_dir
  while IFS= read -r skill_dir; do
    link_skill_runtime "claude" "$CLAUDE_DST" "$skill_dir"
    link_skill_runtime "codex" "$CODEX_DST" "$skill_dir"
  done < <(find "$SKILLS_SRC" -maxdepth 1 -mindepth 1 -type d | sort)
}

cleanup_legacy_paths() {
  cleanup_legacy_path "$CLAUDE_DST/collab" ".claude/collab"
  cleanup_legacy_path "$CLAUDE_DST/skills/feature-interview" ".claude/skills/feature-interview"
  cleanup_legacy_path "$CLAUDE_DST/skills/improve-claude-md" ".claude/skills/improve-claude-md"
  cleanup_legacy_path "$CODEX_DST/skills/feature-interview" ".codex/skills/feature-interview"
  cleanup_legacy_path "$CODEX_DST/skills/improve-claude-md" ".codex/skills/improve-claude-md"
  cleanup_legacy_path "$CODEX_DST/skills/create-pr" ".codex/skills/create-pr"
  cleanup_legacy_path "$CODEX_DST/skills/dvn-web-libraries" ".codex/skills/dvn-web-libraries"
  cleanup_legacy_path "$CODEX_DST/config.shared.toml" ".codex/config.shared.toml"
  cleanup_legacy_path "$CODEX_DST/config.work.toml" ".codex/config.work.toml"
  cleanup_legacy_path "$CODEX_DST/config.personal.toml" ".codex/config.personal.toml"

  for removed_skill in audit cmux improve-agent-md projects qa remove-slop ship; do
    cleanup_removed_skill "$removed_skill"
  done
}

cleanup_legacy_paths
link_claude_payload
link_codex_payload
link_skills

echo "Linked Claude config into $CLAUDE_DST"
echo "Linked Codex config into $CODEX_DST"
echo "Source config came from $DOT_AGENT_SOURCE_ROOT"
echo "Shared state home is $DOT_AGENT_STATE_HOME"
if [[ -d "$BACKUP_ROOT" ]]; then
  echo "Backups stored in $BACKUP_ROOT"
fi
