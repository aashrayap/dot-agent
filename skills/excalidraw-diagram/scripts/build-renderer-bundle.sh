#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"
RENDERER_DIR="$SKILL_DIR/assets/renderer"

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is required to rebuild the Excalidraw renderer bundle." >&2
  exit 1
fi

(
  cd "$RENDERER_DIR"
  npm ci
  npm run build
)
