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

# Single jq call to extract all fields
read -r PR_NUMBER PR_URL TITLE STATE < <(
  echo "$PR_JSON" | jq -r '[.number, .url, .title, .state] | @tsv'
)

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

# Accumulate pages into a temp file to avoid O(n²) re-serialization
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT
echo -n '' > "$TMPFILE"

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

  # Single jq call: extract nodes, hasNextPage, and endCursor together
  read -r HAS_NEXT CURSOR < <(
    echo "$RESPONSE" | jq -r '
      .data.repository.pullRequest.reviewThreads |
      [.pageInfo.hasNextPage, .pageInfo.endCursor] | @tsv'
  )
  echo "$RESPONSE" | jq -c '.data.repository.pullRequest.reviewThreads.nodes[]' >> "$TMPFILE"

  if [[ "$HAS_NEXT" != "true" ]]; then
    break
  fi
done

# ── Single jq pass: filter, group, format ──────────────────────────────────

export PR_URL TITLE PR_NUMBER

RESULT=$(jq -s -r '
  # Filter: unresolved + not outdated
  [ .[] | select(.isResolved == false and .isOutdated == false) ] as $threads |
  ($threads | length) as $count |

  if $count == 0 then
    "\nPR_CONTEXT_START\n" +
    "PR_URL=\(env.PR_URL)\n" +
    "PR_TITLE=\(env.TITLE)\n" +
    "PR_NUMBER=\(env.PR_NUMBER)\n" +
    "THREAD_COUNT=0\n\n" +
    "## PR Review Threads\n" +
    "No unresolved review threads.\n" +
    "PR_CONTEXT_END"
  else
    # Group by path
    ($threads | group_by(.path) | map({
      path: .[0].path,
      thread_count: length,
      threads: .
    })) as $groups |

    "\nPR_CONTEXT_START\n" +
    "PR_URL=\(env.PR_URL)\n" +
    "PR_TITLE=\(env.TITLE)\n" +
    "PR_NUMBER=\(env.PR_NUMBER)\n" +
    "THREAD_COUNT=\($count)\n\n" +
    "## PR Review Threads (\($count) unresolved)\n\n" +
    ($groups | map(
      "### `\(.path)` (\(.thread_count) thread(s))\n" +
      (.threads | map(
        "#### Thread \(.id)\n" +
        "**Line:** \(.line // "file-level")\n" +
        (.comments.nodes | map(
          "> **@\(.author.login)** (\(.createdAt)):\n" +
          "> \(.body | gsub("<details>[\\s\\S]*?</details>"; "") | gsub("\\n{3,}"; "\n\n") | gsub("\n"; "\n> "))\n" +
          (if .diffHunk then "\n```diff\n\(.diffHunk)\n```\n" else "" end)
        ) | join("\n"))
      ) | join("\n---\n\n"))
    ) | join("\n")) +
    "\nPR_CONTEXT_END"
  end
' "$TMPFILE")

echo "$RESULT"
