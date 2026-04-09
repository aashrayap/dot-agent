#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   projects-setup.sh                        → dashboard (list all projects)
#   projects-setup.sh <slug> <action>        → resolve project + requested action
#
# Actions (required when a slug is provided):
#   new    — scaffold a brand-new project
#   update — anything else (view, progress report, completion, restructure, status);
#            the skill figures out intent from the user's raw message
#
# Details live in the user's raw message — this script does not parse them.

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
    echo "Use a different slug, or run with an action other than 'new'."
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
  echo "Create it with: /projects $SLUG new <goal + scope description>"
  exit 1
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

<!-- 1-2 sentences. Outcome delivered to users/leadership, not implementation tactics. -->

## Out of scope

<!-- Only items someone might assume are in scope but aren't. Delete this section if nothing fits. -->

## Blockers & Constraints

## Milestones

<!-- M# identifiers numbered in expected completion order based on the dependency graph. Renumber if blockers shift the order. -->

| # | Milestone | Status |
|---|-----------|--------|

## Sessions

Scoped units of work picked up via \`/spec-new-feature\`. Sessions with no \`Blocked on:\` line are ready to pick up. The dependency graph shows remaining work only.

### Dependency Graph

\`\`\`mermaid
flowchart TB
    %% Group by batch level in invisible subgraphs (b0, b1, ...) with direction LR.
    %% Style each: style b0 fill:none,stroke:none
    %% Color-code nodes by milestone via style directives.
\`\`\`

## Completed

| Session | Completed | Ref |
|---------|-----------|-----|
EOF

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
