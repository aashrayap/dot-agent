#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
RENDER_SCRIPT="$SCRIPT_DIR/render-excalidraw.sh"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dot-agent-excalidraw-test.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

INPUT="$TMP_DIR/sample.excalidraw"
OUTPUT="$TMP_DIR/sample.png"

cat > "$INPUT" <<'JSON'
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "box_one",
      "type": "rectangle",
      "x": 80,
      "y": 80,
      "width": 260,
      "height": 120,
      "angle": 0,
      "strokeColor": "#1f2937",
      "backgroundColor": "#dbeafe",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {"type": 3},
      "seed": 1,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "label_one",
      "type": "text",
      "x": 115,
      "y": 125,
      "width": 190,
      "height": 30,
      "angle": 0,
      "strokeColor": "#111827",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 2,
      "version": 1,
      "versionNonce": 2,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Offline render",
      "fontSize": 24,
      "fontFamily": 3,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": null,
      "originalText": "Offline render",
      "lineHeight": 1.25,
      "baseline": 22
    }
  ],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": null
  },
  "files": {}
}
JSON

"$RENDER_SCRIPT" "$INPUT" "$OUTPUT" --width 900 --scale 1
test -s "$OUTPUT"
python3 - "$OUTPUT" <<'PY'
import sys

path = sys.argv[1]
with open(path, "rb") as handle:
    signature = handle.read(8)
if signature != b"\x89PNG\r\n\x1a\n":
    raise SystemExit(f"expected png signature, got {signature!r}")
print(f"offline renderer smoke passed: {path}")
PY
