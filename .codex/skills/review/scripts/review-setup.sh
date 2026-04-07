#!/usr/bin/env bash
set -euo pipefail

BASE=""
for remote in upstream origin; do
  if git remote show "$remote" &>/dev/null; then
    candidate="$(git remote show "$remote" 2>/dev/null | awk -F': ' '/HEAD branch/ { print $2; exit }')"
    if [[ -n "$candidate" && "$candidate" != "(unknown)" ]]; then
      BASE="$remote/$candidate"
      break
    fi
  fi
done

if [[ -z "$BASE" ]]; then
  for branch in main master develop; do
    if git rev-parse --verify "origin/$branch" &>/dev/null; then
      BASE="origin/$branch"
      break
    fi
    if git rev-parse --verify "$branch" &>/dev/null; then
      BASE="$branch"
      break
    fi
  done
fi

if [[ -z "$BASE" ]]; then
  echo "ERROR: Could not detect a base branch."
  exit 1
fi

CURRENT="$(git branch --show-current 2>/dev/null || git rev-parse --short HEAD)"
MERGE_BASE="$(git merge-base "$BASE" HEAD 2>/dev/null || true)"

if [[ -z "$MERGE_BASE" ]]; then
  echo "ERROR: No common ancestor between $BASE and HEAD."
  exit 1
fi

TMP_CHANGED="$(mktemp)"
trap 'rm -f "$TMP_CHANGED"' EXIT

git diff "$MERGE_BASE"...HEAD --name-only >>"$TMP_CHANGED"
git diff --cached --name-only >>"$TMP_CHANGED"
git diff --name-only >>"$TMP_CHANGED"

CHANGED_FILES=()
while IFS= read -r path; do
  if [[ -n "$path" ]]; then
    CHANGED_FILES+=("$path")
  fi
done < <(sort -u "$TMP_CHANGED")

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No committed, staged, or unstaged changes found."
  exit 1
fi

if [[ $# -gt 0 ]]; then
  FILTERED=()
  for path in "${CHANGED_FILES[@]}"; do
    ext="${path##*.}"
    for wanted in "$@"; do
      if [[ "$ext" == "$wanted" ]]; then
        FILTERED+=("$path")
        break
      fi
    done
  done
  CHANGED_FILES=("${FILTERED[@]}")
fi

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No changed files matched the requested filters."
  exit 1
fi

FILE_COUNT="${#CHANGED_FILES[@]}"
EXTENSIONS="$(printf '%s\n' "${CHANGED_FILES[@]}" | awk -F. 'NF > 1 { print $NF }' | sort -u | tr '\n' ' ' | sed 's/ $//')"
BRANCH_DIFF_STAT="$(git diff "$MERGE_BASE"...HEAD --shortstat -- "${CHANGED_FILES[@]}" 2>/dev/null || true)"
STAGED_DIFF_STAT="$(git diff --cached --shortstat -- "${CHANGED_FILES[@]}" 2>/dev/null || true)"
WORKTREE_DIFF_STAT="$(git diff --shortstat -- "${CHANGED_FILES[@]}" 2>/dev/null || true)"
COMMIT_LOG="$(git log "$MERGE_BASE"...HEAD --oneline --no-merges 2>/dev/null || echo "(no commits)")"
PR_URL="$(gh pr view --json url -q '.url' 2>/dev/null || true)"

echo "REVIEW_CONTEXT_START"
echo "BASE_BRANCH=$BASE"
echo "CURRENT_BRANCH=$CURRENT"
echo "MERGE_BASE=$MERGE_BASE"
echo "FILE_COUNT=$FILE_COUNT"
echo "EXTENSIONS=$EXTENSIONS"
if [[ -n "$PR_URL" ]]; then
  echo "PR_URL=$PR_URL"
fi
echo
echo "## Diff Stats"
if [[ -n "$BRANCH_DIFF_STAT" ]]; then
  echo "branch: $BRANCH_DIFF_STAT"
fi
if [[ -n "$STAGED_DIFF_STAT" ]]; then
  echo "staged: $STAGED_DIFF_STAT"
fi
if [[ -n "$WORKTREE_DIFF_STAT" ]]; then
  echo "worktree: $WORKTREE_DIFF_STAT"
fi
echo
echo "## Commits"
echo "$COMMIT_LOG"
echo
echo "## Changed Files"
printf '%s\n' "${CHANGED_FILES[@]}"
echo "REVIEW_CONTEXT_END"
