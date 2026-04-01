#!/usr/bin/env bash
set -euo pipefail

# Usage: fetch-pr-context.sh
# Detects if the current branch has an open PR, fetches unresolved review threads.
# Outputs structured context or nothing if no PR exists.

# ── Detect PR for current branch ────────────────────────────────────────────

PR_JSON=$(gh pr view --json number,url,title,state,headRefName,baseRefName 2>/dev/null || echo "")

if [[ -z "$PR_JSON" ]]; then
  exit 0
fi

PR_NUMBER=$(echo "$PR_JSON" | jq -r '.number')
PR_URL=$(echo "$PR_JSON" | jq -r '.url')
TITLE=$(echo "$PR_JSON" | jq -r '.title')
STATE=$(echo "$PR_JSON" | jq -r '.state')

# Only process open PRs
if [[ "$STATE" != "OPEN" ]]; then
  exit 0
fi

# ── Parse owner/repo from URL ───────────────────────────────────────────────

if [[ ! "$PR_URL" =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
  exit 0
fi

OWNER="${BASH_REMATCH[1]}"
REPO="${BASH_REMATCH[2]}"

# ── Fetch unresolved review threads ─────────────────────────────────────────

QUERY='query($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $cursor) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          comments(first: 10) {
            nodes {
              id
              body
              author { login }
              diffHunk
              createdAt
            }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}'

ALL_NODES="[]"
CURSOR=""

while true; do
  CURSOR_ARGS=()
  [[ -n "$CURSOR" ]] && CURSOR_ARGS=(-f cursor="$CURSOR")

  RESPONSE=$(gh api graphql \
    -f query="$QUERY" \
    -f owner="$OWNER" \
    -f repo="$REPO" \
    -F pr="$PR_NUMBER" \
    ${CURSOR_ARGS[@]+"${CURSOR_ARGS[@]}"})

  PAGE_NODES=$(echo "$RESPONSE" | jq '.data.repository.pullRequest.reviewThreads.nodes')
  ALL_NODES=$(echo "$ALL_NODES" "$PAGE_NODES" | jq -s '.[0] + .[1]')

  HAS_NEXT=$(echo "$RESPONSE" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')
  if [[ "$HAS_NEXT" != "true" ]]; then
    break
  fi
  CURSOR=$(echo "$RESPONSE" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor')
done

# Shape threads: unresolved + not outdated
THREADS=$(echo "$ALL_NODES" | jq '
  [.[]
   | select(.isResolved == false and .isOutdated == false)
   | {
       thread_id: .id,
       path: .path,
       line: .line,
       start_line: .startLine,
       comments: [.comments.nodes[] | {
         id: .id,
         author: .author.login,
         body: (.body | gsub("<details>[\\s\\S]*?</details>"; "") | gsub("\\n{3,}"; "\n\n")),
         diff_hunk: .diffHunk,
         created_at: .createdAt
       }]
     }
  ]')

THREAD_COUNT=$(echo "$THREADS" | jq 'length')

if [[ "$THREAD_COUNT" -eq 0 ]]; then
  echo ""
  echo "PR_CONTEXT_START"
  echo "PR_URL=$PR_URL"
  echo "PR_TITLE=$TITLE"
  echo "PR_NUMBER=$PR_NUMBER"
  echo "THREAD_COUNT=0"
  echo ""
  echo "## PR Review Threads"
  echo "No unresolved review threads."
  echo "PR_CONTEXT_END"
  exit 0
fi

FILE_GROUPS=$(echo "$THREADS" | jq '
  group_by(.path)
  | map({
      path: .[0].path,
      thread_count: length,
      threads: .
    })')

# ── Output structured context ───────────────────────────────────────────────

echo ""
echo "PR_CONTEXT_START"
echo "PR_URL=$PR_URL"
echo "PR_TITLE=$TITLE"
echo "PR_NUMBER=$PR_NUMBER"
echo "THREAD_COUNT=$THREAD_COUNT"
echo ""
echo "## PR Review Threads ($THREAD_COUNT unresolved)"
echo ""

echo "$FILE_GROUPS" | jq -r '
  .[] |
  "### `\(.path)` (\(.thread_count) thread(s))\n" +
  (.threads | map(
    "#### Thread \(.thread_id)\n" +
    "**Line:** \(.line // "file-level")\n" +
    (.comments | map(
      "> **@\(.author)** (\(.created_at)):\n" +
      "> \(.body | gsub("\n"; "\n> "))\n" +
      (if .diff_hunk then "\n```diff\n\(.diff_hunk)\n```\n" else "" end)
    ) | join("\n"))
  ) | join("\n---\n\n"))
'

echo "PR_CONTEXT_END"
