#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-work}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_FILE="$ROOT_DIR/config.shared.toml"
PROFILE_FILE="$ROOT_DIR/config.${PROFILE}.toml"
TARGET_FILE="$ROOT_DIR/config.toml"

if [[ ! -f "$SHARED_FILE" ]]; then
  echo "ERROR: Missing $SHARED_FILE"
  exit 1
fi

if [[ ! -f "$PROFILE_FILE" ]]; then
  echo "ERROR: Missing $PROFILE_FILE"
  echo "Available profiles:"
  find "$ROOT_DIR" -maxdepth 1 -name 'config.*.toml' -print \
    | sed 's#.*/config\.##; s#\.toml$##' \
    | sort
  exit 1
fi

TMP_FILE="$(mktemp)"
cleanup() {
  rm -f "$TMP_FILE"
}
trap cleanup EXIT

render_file() {
  local file="$1"
  sed "s|__HOME__|$HOME|g" "$file" >>"$TMP_FILE"
  printf '\n' >>"$TMP_FILE"
}

render_file "$SHARED_FILE"
render_file "$PROFILE_FILE"

if [[ -f "$TARGET_FILE" ]]; then
  BACKUP_FILE="$ROOT_DIR/config.toml.local.bak.$(date +%Y%m%d%H%M%S)"
  cp "$TARGET_FILE" "$BACKUP_FILE"
  echo "Backed up existing config.toml to $BACKUP_FILE"
fi

mv "$TMP_FILE" "$TARGET_FILE"
chmod 600 "$TARGET_FILE"

echo "Wrote $TARGET_FILE using profile '$PROFILE'"
