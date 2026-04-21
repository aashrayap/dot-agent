#!/usr/bin/env bash
set -euo pipefail

TODAY=$(date +%Y-%m-%d)
DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
FOCUS_SETUP="${DOT_AGENT_HOME}/skills/focus/scripts/focus-setup.sh"
RECENT_WORK_SCRIPT="${DOT_AGENT_HOME}/skills/morning-sync/scripts/recent-work-summary.py"
WORKING_DOC_SCRIPT="${DOT_AGENT_HOME}/skills/focus/scripts/morning-working-doc.py"

SETUP_OUTPUT="$("$FOCUS_SETUP")"
ROADMAP_FILE="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^ROADMAP_FILE=//p')"
FOCUS_FILE="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^FOCUS_FILE=//p')"
MIGRATED_FOCUS="$(printf "%s\n" "$SETUP_OUTPUT" | sed -n 's/^MIGRATED_FOCUS=//p')"

roadmap_last_touched="$(head -10 "$ROADMAP_FILE" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")"
if [[ "$roadmap_last_touched" == "$TODAY" ]]; then
  roadmap_stale="no"
else
  roadmap_stale="yes"
fi

focus_last_touched="$(head -10 "$FOCUS_FILE" | grep -m1 'last_touched:' | sed 's/.*last_touched: *//' || echo "unknown")"
if [[ "$focus_last_touched" == "$TODAY" ]]; then
  focus_stale="no"
else
  focus_stale="yes"
fi

echo "ROADMAP_FILE=$ROADMAP_FILE"
echo "ROADMAP_LAST_TOUCHED=$roadmap_last_touched"
echo "ROADMAP_STALE=$roadmap_stale"
echo "FOCUS_FILE=$FOCUS_FILE"
echo "FOCUS_LAST_TOUCHED=$focus_last_touched"
echo "FOCUS_STALE=$focus_stale"
echo "MIGRATED_FOCUS=$MIGRATED_FOCUS"
echo "ROADMAP_SOURCE=human-roadmap"
echo "PROJECT_STATE_NORMAL_READS=recent-work-summary-only"
echo "RECENT_WORK_SCRIPT=$RECENT_WORK_SCRIPT"
echo "WORKING_DOC_SCRIPT=$WORKING_DOC_SCRIPT"
