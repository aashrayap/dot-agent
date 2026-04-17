#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  render-excalidraw.sh <input.excalidraw> [output.png] [--scale N] [--width PX]

Renders an Excalidraw JSON file to PNG using the upstream renderer cached under
~/.dot-agent/state/tools/excalidraw-diagram-skill.
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

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required to fetch the Excalidraw renderer." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required to run the Excalidraw renderer." >&2
  exit 1
fi

DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
TOOLS_DIR="$DOT_AGENT_STATE_HOME/tools"
RENDERER_DIR="$TOOLS_DIR/excalidraw-diagram-skill"
RENDERER_REF_DIR="$RENDERER_DIR/references"
RENDERER_URL="https://github.com/coleam00/excalidraw-diagram-skill.git"

mkdir -p "$TOOLS_DIR"

if [[ ! -d "$RENDERER_DIR/.git" ]]; then
  git clone --depth 1 "$RENDERER_URL" "$RENDERER_DIR"
elif [[ "${EXCALIDRAW_RENDERER_UPDATE:-0}" == "1" ]]; then
  git -C "$RENDERER_DIR" pull --ff-only
fi

if [[ ! -f "$RENDERER_REF_DIR/render_excalidraw.py" ]]; then
  echo "ERROR: renderer script missing: $RENDERER_REF_DIR/render_excalidraw.py" >&2
  exit 1
fi

(
  cd "$RENDERER_REF_DIR"
  uv sync
  if [[ ! -f .playwright-chromium-ready ]]; then
    uv run playwright install chromium
    touch .playwright-chromium-ready
  fi

  if [[ -n "$OUTPUT" ]]; then
    uv run python render_excalidraw.py "$INPUT" --output "$OUTPUT" --scale "$SCALE" --width "$WIDTH"
  else
    uv run python render_excalidraw.py "$INPUT" --scale "$SCALE" --width "$WIDTH"
  fi
)
