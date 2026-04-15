#!/usr/bin/env bash
set -euo pipefail

TODAY=$(date +%Y-%m-%d)
DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
FOCUS_SETUP="${DOT_AGENT_HOME}/skills/focus/scripts/focus-setup.sh"

SETUP_OUTPUT="$("$FOCUS_SETUP")"
FOCUS_FILE="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^FOCUS_FILE=//p')"
PROJECTS_DIR="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^PROJECTS_DIR=//p')"
MIGRATED_FOCUS="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^MIGRATED_FOCUS=//p')"

focus_last_touched="$(head -10 "$FOCUS_FILE" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")"
if [[ "$focus_last_touched" == "$TODAY" ]]; then
  focus_stale="no"
else
  focus_stale="yes"
fi

echo "FOCUS_FILE=$FOCUS_FILE"
echo "FOCUS_LAST_TOUCHED=$focus_last_touched"
echo "FOCUS_STALE=$focus_stale"
echo "MIGRATED_FOCUS=$MIGRATED_FOCUS"
echo "ACTIVE_PROJECTS_BEGIN"

if [[ -d "$PROJECTS_DIR" ]]; then
  for dir in "$PROJECTS_DIR"/*/; do
    [[ -d "$dir" ]] || continue

    slug="$(basename "$dir")"
    project_file="${dir}project.md"
    execution_file="${dir}execution.md"

    [[ -f "$project_file" ]] || continue

    status="$(head -10 "$project_file" | grep -m1 'status:' | sed 's/.*status: *//' || echo "unknown")"
    if [[ "$status" == "complete" ]]; then
      continue
    fi

    project_touched="$(head -10 "$project_file" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")"
    execution_touched="missing"
    if [[ -f "$execution_file" ]]; then
      execution_touched="$(head -10 "$execution_file" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")"
    fi

    echo "${slug}|${status}|${project_touched}|${execution_touched}|${project_file}|${execution_file}"
  done
fi

echo "ACTIVE_PROJECTS_END"
