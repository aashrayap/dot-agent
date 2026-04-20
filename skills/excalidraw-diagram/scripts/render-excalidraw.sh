#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  render-excalidraw.sh <input.excalidraw> [output.png] [--scale N] [--width PX]

Renders an Excalidraw JSON file to PNG using the skill's tracked offline
renderer assets.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

INPUT="$1"
shift

OUTPUT=""
SCALE="2"
WIDTH="5200"

if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  OUTPUT="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scale)
      SCALE="${2:?missing value for --scale}"
      shift 2
      ;;
    --width)
      WIDTH="${2:?missing value for --width}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: input file not found: $INPUT" >&2
  exit 1
fi

INPUT="$(cd "$(dirname "$INPUT")" && pwd -P)/$(basename "$INPUT")"
if [[ -n "$OUTPUT" ]]; then
  mkdir -p "$(dirname "$OUTPUT")"
  OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd -P)/$(basename "$OUTPUT")"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required to run the Excalidraw renderer." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"
RENDERER_SRC_DIR="$SKILL_DIR/assets/renderer"

DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
TOOLS_DIR="$DOT_AGENT_STATE_HOME/tools"
RENDERER_STATE_DIR="$TOOLS_DIR/excalidraw-diagram-renderer"
RENDERER_VENV="$RENDERER_STATE_DIR/.venv"
PLAYWRIGHT_BROWSERS_PATH="$RENDERER_STATE_DIR/playwright-browsers"

if [[ ! -d "$RENDERER_SRC_DIR" ]]; then
  echo "ERROR: renderer assets missing: $RENDERER_SRC_DIR" >&2
  exit 1
fi

if [[ ! -f "$RENDERER_SRC_DIR/render_excalidraw.py" ]]; then
  echo "ERROR: renderer script missing: $RENDERER_SRC_DIR/render_excalidraw.py" >&2
  exit 1
fi

if [[ ! -f "$RENDERER_SRC_DIR/dist/excalidraw-export.bundle.js" ]]; then
  echo "ERROR: local Excalidraw browser bundle missing." >&2
  echo "Run: $SKILL_DIR/scripts/build-renderer-bundle.sh" >&2
  exit 1
fi

mkdir -p "$RENDERER_STATE_DIR" "$PLAYWRIGHT_BROWSERS_PATH"

(
  cd "$RENDERER_SRC_DIR"
  UV_PROJECT_ENVIRONMENT="$RENDERER_VENV" uv sync --frozen
  if [[ ! -f "$RENDERER_STATE_DIR/.playwright-chromium-ready" ]]; then
    PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" \
      UV_PROJECT_ENVIRONMENT="$RENDERER_VENV" \
      uv run playwright install chromium
    touch "$RENDERER_STATE_DIR/.playwright-chromium-ready"
  fi

  if [[ -n "$OUTPUT" ]]; then
    PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" \
      UV_PROJECT_ENVIRONMENT="$RENDERER_VENV" \
      uv run python render_excalidraw.py "$INPUT" --output "$OUTPUT" --scale "$SCALE" --width "$WIDTH"
  else
    PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" \
      UV_PROJECT_ENVIRONMENT="$RENDERER_VENV" \
      uv run python render_excalidraw.py "$INPUT" --scale "$SCALE" --width "$WIDTH"
  fi
)
