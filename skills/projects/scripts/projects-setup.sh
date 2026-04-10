#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   projects-setup.sh                        → dashboard (list all projects)
#   projects-setup.sh <slug> <action>        → resolve project + requested action
#
# Actions (required when a slug is provided):
#   new    — scaffold a brand-new project
#   update — anything else (view, progress, completion, restructure)

TODAY=$(date +%Y-%m-%d)
NOW=$(date +"%Y-%m-%d %H:%M:%S")
PROJECTS_DIR=".claude/projects"
VALID_ACTIONS="new update"

# --- Helpers ---

print_status() {
  local pf="$1"
  local status last_touched
  status=$(head -10 "$pf" | grep -m1 'status:' | sed 's/.*status: *//' || echo "unknown")
  last_touched=$(head -10 "$pf" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")
  echo "  status: $status"
  echo "  last_touched: $last_touched"
}

# --- DASHBOARD (no args) ---
if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "MODE=dashboard"
  echo ""
  if [[ ! -d "$PROJECTS_DIR" ]] || [[ -z "$(ls -A "$PROJECTS_DIR" 2>/dev/null)" ]]; then
    echo "No projects yet."
  else
    for dir in "$PROJECTS_DIR"/*/; do
      [[ -d "$dir" ]] || continue
      slug=$(basename "$dir")
      pf="${dir}project.md"
      if [[ -f "$pf" ]]; then
        echo "- $slug"
        print_status "$pf"
        echo ""
      fi
    done
  fi
  exit 0
fi

SLUG="$1"

# Validate kebab-case
if [[ ! "$SLUG" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: '$SLUG' is not valid kebab-case."
  echo "Must be lowercase letters/digits/hyphens, start with a letter."
  exit 1
fi

# Action is required when a slug is provided
if [[ $# -lt 2 || -z "${2:-}" ]]; then
  echo "ERROR: Missing action."
  echo "Usage: /projects $SLUG <new|update> [details...]"
  exit 1
fi

ACTION="$2"

# Validate action
if ! echo " $VALID_ACTIONS " | grep -q " $ACTION "; then
  echo "ERROR: Unknown action '$ACTION'."
  echo "Valid actions: $VALID_ACTIONS"
  exit 1
fi

PROJECT_DIR="${PROJECTS_DIR}/${SLUG}"
PROJECT_FILE="${PROJECT_DIR}/project.md"
AUDIT_LOG="${PROJECT_DIR}/AUDIT_LOG.md"

# --- EXISTS: return project info ---
if [[ -f "$PROJECT_FILE" ]]; then
  if [[ "$ACTION" == "new" ]]; then
    echo "ERROR: Project '$SLUG' already exists."
    echo "Use a different slug, or run with 'update'."
    exit 1
  fi
  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "PROJECT_SLUG=$SLUG"
  echo "PROJECT_FILE=$PROJECT_FILE"
  echo "AUDIT_LOG=$AUDIT_LOG"
  echo "ACTION=$ACTION"
  echo "MODE=existing"
  echo ""
  print_status "$PROJECT_FILE"
  exit 0
fi

# --- Project doesn't exist ---
if [[ "$ACTION" != "new" ]]; then
  echo "ERROR: Project '$SLUG' does not exist."
  echo "Create it with: /projects $SLUG new <goal description>"
  exit 1
fi

# --- NEW: scaffold and return project info ---
mkdir -p "$PROJECT_DIR"

cat > "$PROJECT_FILE" << 'TEMPLATE'
---
status: active
started: DATE_PLACEHOLDER
last_touched: DATE_PLACEHOLDER
---

# SLUG_PLACEHOLDER

<!-- 1-2 sentence goal. Outcome delivered, not implementation. -->

## Plan

<!--
Nested TODO list. Milestones contain sessions. Format:

- [ ] **M1 — Milestone Name** 🟦
  - [ ] S01 — Session name
    - Blocked on: [S02](#s02)
    - Blocking: [S03](#s03)
  - [ ] S02 — Session name
    - Blocking: [S01](#s01), [S03](#s03)
  - [x] S03 — Done session — [PR #12](...)
- [x] **M2 — Other Milestone** 🟩
  - [x] S04 — Done — [DEF-123](...)

Rules:
- [x] marks completion. Check milestone when all its sessions are done.
- Append ref (PR, ticket) to completed sessions.
- Blocked on / Blocking as sub-bullets. Omit if empty.
- On completion: remove blocker/blocking lines, update other sessions accordingly.

Milestone emoji color key: 🟦 🟪 🟧 🟩 🟥 🟨 (reuse if >6).
-->

## Dependencies

<!--
Mermaid flowchart TB — remaining work only. Remove completed sessions entirely.
Group by batch level in invisible subgraphs. Transitive reduction only.

Color-code nodes by milestone:
  🟦 fill:#60a5fa,stroke:#1e40af,color:#1e3a5f
  🟪 fill:#c084fc,stroke:#6b21a8,color:#3b0764
  🟧 fill:#fb923c,stroke:#9a3412,color:#431407
  🟩 fill:#4ade80,stroke:#166534,color:#052e16
  🟥 fill:#f87171,stroke:#991b1b,color:#450a0a
  🟨 fill:#facc15,stroke:#854d0e,color:#422006

Example:
  subgraph b0[" "]
      direction LR
      s01([S01 Short name])
      s02([S02 Short name])
  end
  style b0 fill:none,stroke:none
  style s01 fill:#60a5fa,stroke:#1e40af,color:#1e3a5f
-->

```mermaid
flowchart TB
```
TEMPLATE

# Replace placeholders
sed -i '' "s/DATE_PLACEHOLDER/$TODAY/g" "$PROJECT_FILE"
sed -i '' "s/SLUG_PLACEHOLDER/$SLUG/g" "$PROJECT_FILE"

printf "# Audit Log: %s\n\n## %s\n\nProject created.\n\n" "$SLUG" "$NOW" > "$AUDIT_LOG"

echo "PROJECT_DIR=$PROJECT_DIR"
echo "PROJECT_SLUG=$SLUG"
echo "PROJECT_FILE=$PROJECT_FILE"
echo "AUDIT_LOG=$AUDIT_LOG"
echo "ACTION=new"
echo "MODE=new"
echo ""
echo "Scaffolded $PROJECT_FILE"
exit 0
