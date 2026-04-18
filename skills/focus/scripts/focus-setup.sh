#!/usr/bin/env bash
set -euo pipefail

TODAY=$(date +%Y-%m-%d)
DOT_AGENT_HOME="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
DOT_AGENT_STATE_HOME="${DOT_AGENT_STATE_HOME:-$DOT_AGENT_HOME/state}"
COLLAB_DIR="${DOT_AGENT_STATE_HOME}/collab"
FOCUS_FILE="${COLLAB_DIR}/focus.md"
ROADMAP_SCRIPT="${DOT_AGENT_HOME}/skills/focus/scripts/roadmap.py"

mkdir -p "$COLLAB_DIR"

CREATED_FOCUS="no"
MIGRATED_FOCUS="no"

extract_section() {
  local heading="$1"
  awk -v heading="## ${heading}" '
    $0 == heading { in_section=1; next }
    in_section && /^## / { exit }
    in_section { print }
  ' "$FOCUS_FILE"
}

list_items_or_blank() {
  local content="$1"
  local items
  items="$(printf "%s\n" "$content" | sed -n 's/^- /- /p' | sed '/^- None$/d')"
  if [[ -n "$items" ]]; then
    printf "%s\n" "$items"
  fi
}

if [[ ! -f "$FOCUS_FILE" ]]; then
  cat > "$FOCUS_FILE" << EOF
---
status: active
started: $TODAY
last_touched: $TODAY
wip_limit: 1
---

# Focus

## Current Focus

None set yet.

## Now

- None

## Next

- None

## Later / Parking Lot

- None

## Blockers

- None

## Recent Shifts

| Date | From | To | Why |
|------|------|----|-----|
EOF
  CREATED_FOCUS="yes"
elif grep -q '^## Focus$' "$FOCUS_FILE" && grep -q '^## Queued$' "$FOCUS_FILE"; then
  backup_file="${COLLAB_DIR}/focus.legacy.$(date +%Y%m%d%H%M%S).md"
  cp "$FOCUS_FILE" "$backup_file"

  focus_text="$(extract_section "Focus" | sed '/^$/d')"
  queued_items="$(list_items_or_blank "$(extract_section "Queued")")"
  in_progress_items="$(list_items_or_blank "$(extract_section "In Progress")")"
  done_items="$(list_items_or_blank "$(extract_section "Done")")"

  current_focus="$(printf "%s\n" "$in_progress_items" | sed -n '1s/^- //p')"
  if [[ -z "$current_focus" ]]; then
    current_focus="$(printf "%s\n" "$focus_text" | sed -n '1p')"
  fi
  [[ -n "$current_focus" ]] || current_focus="None set yet."

  cat > "$FOCUS_FILE" << EOF
---
status: active
started: $TODAY
last_touched: $TODAY
wip_limit: 1
---

# Focus

## Current Focus

$current_focus

## Now
${in_progress_items:-"- None"}

## Next
${queued_items:-"- None"}

## Later / Parking Lot
- None

## Blockers
- None

## Recent Shifts

| Date | From | To | Why |
|------|------|----|-----|
EOF
  if [[ -n "$done_items" ]]; then
    {
      printf "\n"
      printf "<!-- Legacy Done items preserved from migration:\n"
      printf "%s\n" "$done_items"
      printf "-->\n"
    } >> "$FOCUS_FILE"
  fi
  MIGRATED_FOCUS="yes"
fi

ROADMAP_OUTPUT="$(python3 "$ROADMAP_SCRIPT" setup)"
ROADMAP_FILE="$(printf "%s\n" "$ROADMAP_OUTPUT" | sed -n 's/^ROADMAP_FILE=//p')"

echo "ROADMAP_FILE=$ROADMAP_FILE"
echo "FOCUS_FILE=$FOCUS_FILE"
echo "CREATED_FOCUS=$CREATED_FOCUS"
echo "MIGRATED_FOCUS=$MIGRATED_FOCUS"
echo "PROJECT_STATE_NORMAL_READS=no"
