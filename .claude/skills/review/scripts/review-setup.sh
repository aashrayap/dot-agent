#!/usr/bin/env bash
set -euo pipefail

# Usage: review-setup.sh
# No arguments. Run from within the target repo.
# Returns: branch info, merge base, file list, diff stats, commit log, PR link.

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
  echo "ERROR: Could not detect base branch."
  exit 1
fi

CURRENT=$(git branch --show-current 2>/dev/null || git rev-parse --short HEAD)
MERGE_BASE=$(git merge-base "$BASE" HEAD 2>/dev/null || echo "")

if [[ -z "$MERGE_BASE" ]]; then
  echo "ERROR: No common ancestor between $BASE and HEAD."
  exit 1
fi

# --- Changed files ---
CHANGED_FILES=$(git diff "$MERGE_BASE"...HEAD --name-only 2>/dev/null || true)

if [[ -z "$CHANGED_FILES" ]]; then
  echo "ERROR: No changed files found between $BASE and $CURRENT."
  exit 1
fi

FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
UNIQUE_EXTS=$(echo "$CHANGED_FILES" | sed 's/.*\.//' | sort -u | tr '\n' ' ' | sed 's/ $//')

# --- Diff stats (counts only) ---
DIFF_STAT=$(git diff "$MERGE_BASE"...HEAD --shortstat 2>/dev/null || echo "")

# --- Commit log ---
COMMIT_LOG=$(git log "$MERGE_BASE"...HEAD --oneline --no-merges 2>/dev/null || echo "(no commits)")

# --- PR link (if any) ---
PR_URL=$(gh pr view --json url -q '.url' 2>/dev/null || echo "")

# --- Output ---
echo "REVIEW_CONTEXT_START"
echo "BASE_BRANCH=$BASE"
echo "CURRENT_BRANCH=$CURRENT"
echo "MERGE_BASE=$MERGE_BASE"
echo "FILE_COUNT=$FILE_COUNT"
echo "EXTENSIONS=$UNIQUE_EXTS"
if [[ -n "$PR_URL" ]]; then
  echo "PR_URL=$PR_URL"
fi
echo ""
echo "## Diff Stats"
echo "$DIFF_STAT"
echo ""
echo "## Commits"
echo "$COMMIT_LOG"
echo ""
echo "## Changed Files"
echo "$CHANGED_FILES"
echo "REVIEW_CONTEXT_END"
