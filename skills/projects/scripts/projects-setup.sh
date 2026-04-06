#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   projects-setup.sh              → dashboard (list all projects)
#   projects-setup.sh <slug>       → return existing project info, or scaffold if new

TODAY=$(date +%Y-%m-%d)
NOW=$(date +"%Y-%m-%d %H:%M:%S")
PROJECTS_DIR=".claude/projects"

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

PROJECT_DIR="${PROJECTS_DIR}/${SLUG}"
PROJECT_FILE="${PROJECT_DIR}/project.md"
AUDIT_LOG="${PROJECT_DIR}/AUDIT_LOG.md"

# --- EXISTS: return project info ---
if [[ -f "$PROJECT_FILE" ]]; then
  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "PROJECT_SLUG=$SLUG"
  echo "PROJECT_FILE=$PROJECT_FILE"
  echo "AUDIT_LOG=$AUDIT_LOG"
  echo "MODE=existing"
  echo ""
  print_status "$PROJECT_FILE"
  exit 0
fi

# --- NEW: scaffold and return project info ---
mkdir -p "$PROJECT_DIR"

cat > "$PROJECT_FILE" << EOF
---
status: active
started: $TODAY
last_touched: $TODAY
---

# ${SLUG}

## Goal

## Scope

**In scope:**
-

**Out of scope:**
-

## Blockers & Constraints

## Milestones

| # | Milestone | Status |
|---|-----------|--------|

## Sessions

Sessions are scoped units of work picked up via \`/spec-new-feature\`. Each session has dependencies — only unblocked sessions can be started.

### Dependency Graph

\`\`\`mermaid
flowchart TB
    %% No subgraphs — arrows determine depth. Color-code nodes by milestone.
\`\`\`

### Definitions
EOF

printf "# Audit Log: %s\n\n## %s\n\nProject created.\n\n" "$SLUG" "$NOW" > "$AUDIT_LOG"

echo "PROJECT_DIR=$PROJECT_DIR"
echo "PROJECT_SLUG=$SLUG"
echo "PROJECT_FILE=$PROJECT_FILE"
echo "AUDIT_LOG=$AUDIT_LOG"
echo "MODE=new"
echo ""
echo "Scaffolded $PROJECT_FILE"
exit 0
