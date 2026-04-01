#!/usr/bin/env bash
set -euo pipefail

# Usage: review-setup.sh [ext1 ext2 ...]
# Detects base branch, computes diff, groups changed files by extension.
# If extensions are provided, only includes files matching those extensions.

EXTENSIONS=("$@")

# --- Detect base branch ---
BASE=""
for remote in upstream origin; do
  if git remote show "$remote" &>/dev/null; then
    candidate=$(git remote show "$remote" 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
    if [[ -n "$candidate" && "$candidate" != "(unknown)" ]]; then
      BASE="${remote}/${candidate}"
      break
    fi
  fi
done

if [[ -z "$BASE" ]]; then
  for branch in main master develop; do
    if git rev-parse --verify "origin/$branch" &>/dev/null; then
      BASE="origin/$branch"
      break
    elif git rev-parse --verify "$branch" &>/dev/null; then
      BASE="$branch"
      break
    fi
  done
fi

if [[ -z "$BASE" ]]; then
  echo "ERROR: Could not detect base branch. Please specify manually."
  exit 1
fi

CURRENT=$(git branch --show-current 2>/dev/null || git rev-parse --short HEAD)
MERGE_BASE=$(git merge-base "$BASE" HEAD 2>/dev/null || echo "")

if [[ -z "$MERGE_BASE" ]]; then
  echo "ERROR: No common ancestor between $BASE and HEAD."
  exit 1
fi

# --- Get all changed files ---
ALL_CHANGED=$(git diff "$MERGE_BASE"...HEAD --name-only 2>/dev/null || true)

if [[ -z "$ALL_CHANGED" ]]; then
  echo "ERROR: No changed files found between $BASE and $CURRENT."
  exit 1
fi

# --- Filter by extensions if provided ---
if [[ ${#EXTENSIONS[@]} -gt 0 ]]; then
  CHANGED_FILES=""
  for file in $ALL_CHANGED; do
    ext="${file##*.}"
    for filter_ext in "${EXTENSIONS[@]}"; do
      # Strip leading dot if user passed ".sol" instead of "sol"
      filter_ext="${filter_ext#.}"
      if [[ "$ext" == "$filter_ext" ]]; then
        CHANGED_FILES="${CHANGED_FILES}${file}"$'\n'
        break
      fi
    done
  done
  CHANGED_FILES=$(echo "$CHANGED_FILES" | sed '/^$/d')

  if [[ -z "$CHANGED_FILES" ]]; then
    echo "ERROR: No changed files matching extensions: ${EXTENSIONS[*]}"
    exit 1
  fi
else
  CHANGED_FILES="$ALL_CHANGED"
fi

FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')

# --- Group files by extension ---
declare -A EXT_FILES
declare -A EXT_COUNTS

while IFS= read -r file; do
  ext="${file##*.}"
  EXT_FILES[$ext]="${EXT_FILES[$ext]:-}${file}\n"
  EXT_COUNTS[$ext]=$(( ${EXT_COUNTS[$ext]:-0} + 1 ))
done <<< "$CHANGED_FILES"

# --- Diff stats ---
DIFF_STAT=$(git diff "$MERGE_BASE"...HEAD --stat -- $CHANGED_FILES 2>/dev/null | tail -1)

# --- Commit log ---
COMMIT_LOG=$(git log "$MERGE_BASE"...HEAD --oneline --no-merges 2>/dev/null || echo "(no commits)")
COMMIT_COUNT=$(echo "$COMMIT_LOG" | grep -c . || echo "0")

# --- Output structured context ---
echo "REVIEW_CONTEXT_START"
echo "BASE_BRANCH=$BASE"
echo "CURRENT_BRANCH=$CURRENT"
echo "MERGE_BASE=$MERGE_BASE"
echo "FILE_COUNT=$FILE_COUNT"
echo "COMMIT_COUNT=$COMMIT_COUNT"
if [[ ${#EXTENSIONS[@]} -gt 0 ]]; then
  echo "FILTER=${EXTENSIONS[*]}"
fi
echo ""
echo "## Diff Stats"
echo "$DIFF_STAT"
echo ""
echo "## Commits"
echo "$COMMIT_LOG"
echo ""
echo "## Changed Files by Extension"
for ext in $(echo "${!EXT_COUNTS[@]}" | tr ' ' '\n' | sort); do
  echo ""
  echo "### .${ext} (${EXT_COUNTS[$ext]} files)"
  echo -e "${EXT_FILES[$ext]}" | sed '/^$/d'
done
echo ""

# --- Full diff (only for matched files) ---
echo "## Full Diff"
echo '```diff'
git diff "$MERGE_BASE"...HEAD -- $CHANGED_FILES 2>/dev/null
echo '```'
echo "REVIEW_CONTEXT_END"

# --- PR review threads (conditional) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/fetch-pr-context.sh"
