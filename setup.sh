#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-work}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOT_AGENT_HOME="${DOT_AGENT_HOME:-$REPO_ROOT}"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
CLAUDE_SRC="$REPO_ROOT/claude"
CODEX_SRC="$REPO_ROOT/codex"
SKILLS_SRC="$REPO_ROOT/skills"
CLAUDE_DST="$HOME/.claude"
CODEX_DST="$HOME/.codex"
BACKUP_ROOT="$DOT_AGENT_STATE_HOME/backups/setup/$(date +%Y%m%d%H%M%S)"

mkdir -p \
  "$CLAUDE_DST/skills" \
  "$CODEX_DST/skills" \
  "$DOT_AGENT_STATE_HOME/collab" \
  "$DOT_AGENT_STATE_HOME/projects" \
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

cleanup_legacy_path() {
  local path="$1"
  local rel="$2"

  if [[ -e "$path" || -L "$path" ]]; then
    backup_path "$path" "$rel"
  fi
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

render_codex_config() {
  local shared_file="$CODEX_SRC/config.shared.toml"
  local profile_file="$CODEX_SRC/config.${PROFILE}.toml"
  local target_file="$CODEX_DST/config.toml"
  local tmp_file

  if [[ ! -f "$profile_file" ]]; then
    echo "ERROR: Missing Codex profile: $profile_file"
    exit 1
  fi

  tmp_file="$(mktemp)"
  trap 'rm -f "$tmp_file"' RETURN

  sed "s|__HOME__|$HOME|g" "$shared_file" >"$tmp_file"
  printf '\n' >>"$tmp_file"
  sed "s|__HOME__|$HOME|g" "$profile_file" >>"$tmp_file"

  if [[ -f "$target_file" ]] && cmp -s "$tmp_file" "$target_file"; then
    rm -f "$tmp_file"
    trap - RETURN
    return
  fi

  backup_path "$target_file" ".codex/config.toml"
  mkdir -p "$(dirname "$target_file")"
  mv "$tmp_file" "$target_file"
  chmod 600 "$target_file"
  trap - RETURN
}

ensure_codex_rules() {
  local dst_dir="$CODEX_DST/rules"
  mkdir -p "$dst_dir"

  for src_file in "$CODEX_SRC"/rules/*; do
    local name
    local dst_file

    [[ -e "$src_file" ]] || continue
    name="$(basename "$src_file")"
    dst_file="$dst_dir/$name"
    if [[ ! -e "$dst_file" ]]; then
      cp "$src_file" "$dst_file"
    fi
  done
}

link_codex_payload() {
  backup_and_link "$CODEX_SRC/AGENTS.md" "$CODEX_DST/AGENTS.md" ".codex/AGENTS.md"
  backup_and_link "$CODEX_SRC/config.shared.toml" "$CODEX_DST/config.shared.toml" ".codex/config.shared.toml"
  backup_and_link "$CODEX_SRC/config.work.toml" "$CODEX_DST/config.work.toml" ".codex/config.work.toml"
  backup_and_link "$CODEX_SRC/config.personal.toml" "$CODEX_DST/config.personal.toml" ".codex/config.personal.toml"
  render_codex_config
  ensure_codex_rules
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
  cleanup_legacy_path "$CODEX_DST/skills/feature-interview" ".codex/skills/feature-interview"
}

cleanup_legacy_paths
link_claude_payload
link_codex_payload
link_skills

echo "Linked Claude config into $CLAUDE_DST"
echo "Linked Codex config into $CODEX_DST using profile '$PROFILE'"
echo "Shared state home is $DOT_AGENT_STATE_HOME"
if [[ -d "$BACKUP_ROOT" ]]; then
  echo "Backups stored in $BACKUP_ROOT"
fi
