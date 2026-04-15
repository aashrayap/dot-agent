#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   projects-setup.sh                        -> dashboard (list all projects)
#   projects-setup.sh <slug>                 -> return existing project info, or scaffold if new
#   projects-setup.sh --ensure-execution <slug> -> ensure execution.md exists for an existing project

TODAY=$(date +%Y-%m-%d)
NOW=$(date +"%Y-%m-%d %H:%M:%S")
DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
PROJECTS_DIR="${DOT_AGENT_STATE_HOME}/projects"
mkdir -p "$PROJECTS_DIR"
ENSURE_EXECUTION="no"

print_status() {
  local pf="$1"
  local status last_touched
  status=$(head -10 "$pf" | grep -m1 'status:' | sed 's/.*status: *//' || echo "unknown")
  last_touched=$(head -10 "$pf" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")
  echo "  status: $status"
  echo "  last_touched: $last_touched"
}

write_execution_file() {
  local execution_file="$1"
  local status="$2"
  local started="$3"
  local last_touched="$4"
  local progress_summary="$5"
  local follow_up="$6"

  cat > "$execution_file" << EOF
---
status: $status
started: $started
last_touched: $last_touched
---

# Execution Memory

## Progress Summary

$progress_summary

## PRs

| PR | Status | Scope | Notes |
|----|--------|-------|-------|

## Pivots & Changes

| Date | Change | Why |
|------|--------|-----|

## Effort Summary

| Metric | Value |
|--------|-------|

## Open Follow-ups

$follow_up
EOF
}

while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --ensure-execution)
      ENSURE_EXECUTION="yes"
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "ERROR: unknown option '$1'"
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  if [[ "$ENSURE_EXECUTION" == "yes" ]]; then
    echo "ERROR: --ensure-execution requires a project slug."
    exit 1
  fi
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

if [[ ! "$SLUG" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: '$SLUG' is not valid kebab-case."
  echo "Must be lowercase letters/digits/hyphens, start with a letter."
  exit 1
fi

PROJECT_DIR="${PROJECTS_DIR}/${SLUG}"
PROJECT_FILE="${PROJECT_DIR}/project.md"
EXECUTION_FILE="${PROJECT_DIR}/execution.md"
AUDIT_LOG="${PROJECT_DIR}/AUDIT_LOG.md"

if [[ -f "$PROJECT_FILE" ]]; then
  if [[ ! -f "$EXECUTION_FILE" && "$ENSURE_EXECUTION" == "yes" ]]; then
    project_status="$(head -10 "$PROJECT_FILE" | grep -m1 'status:' | sed 's/.*status: *//' || echo "active")"
    project_started="$(head -10 "$PROJECT_FILE" | grep -m1 'started:' | sed 's/.*started: *//' || echo "$TODAY")"
    write_execution_file \
      "$EXECUTION_FILE" \
      "$project_status" \
      "$project_started" \
      "$TODAY" \
      "Backfilled execution memory on $TODAY for an existing project. Historical execution details have not been reconstructed yet." \
      "- Backfill historical PRs and pivots if they matter."
  fi

  echo "PROJECT_DIR=$PROJECT_DIR"
  echo "PROJECT_SLUG=$SLUG"
  echo "PROJECT_FILE=$PROJECT_FILE"
  echo "EXECUTION_FILE=$EXECUTION_FILE"
  if [[ -f "$EXECUTION_FILE" ]]; then
    echo "EXECUTION_EXISTS=yes"
  else
    echo "EXECUTION_EXISTS=no"
  fi
  echo "AUDIT_LOG=$AUDIT_LOG"
  echo "MODE=existing"
  echo ""
  print_status "$PROJECT_FILE"
  exit 0
fi

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

Sessions are delivery slices picked up via \`/spec-new-feature\` or direct execution.
Create a session only when it deserves its own completion row, dependency edge, or handoff.
Keep \`## Available Sessions\` to one clear next slice when possible.

### Dependency Graph (Optional)

\`\`\`mermaid
flowchart TB
    %% Add this only when 3+ live slices or real sequencing make a graph useful.
    %% Group by batch level in invisible subgraphs (b0, b1, ...) with direction LR.
    %% Style each: style b0 fill:none,stroke:none
    %% Color-code nodes by milestone via style directives.
\`\`\`

## Available Sessions

## Blocked Sessions

## Completed

| Session | Completed | Ref |
|---------|-----------|-----|
EOF

printf "# Audit Log: %s\n\n## %s\n\nProject created.\n\n" "$SLUG" "$NOW" > "$AUDIT_LOG"

write_execution_file \
  "$EXECUTION_FILE" \
  "active" \
  "$TODAY" \
  "$TODAY" \
  "Project scaffolded on $TODAY. Add execution reality here once work begins." \
  ""

echo "PROJECT_DIR=$PROJECT_DIR"
echo "PROJECT_SLUG=$SLUG"
echo "PROJECT_FILE=$PROJECT_FILE"
echo "EXECUTION_FILE=$EXECUTION_FILE"
echo "EXECUTION_EXISTS=yes"
echo "AUDIT_LOG=$AUDIT_LOG"
echo "MODE=new"
echo ""
echo "Scaffolded $PROJECT_FILE"
exit 0
