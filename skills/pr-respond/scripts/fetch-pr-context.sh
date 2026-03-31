#!/usr/bin/env bash
set -euo pipefail

# Usage: fetch-pr-context.sh <pr-url>
# Fetches PR metadata, unresolved review threads, and repo tooling info.
# Outputs structured context for dynamic injection into the skill.

PR_URL="${1:?Usage: fetch-pr-context.sh <pr-url>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# ── Parse PR URL ──────────────────────────────────────────────────────────────

if [[ ! "$PR_URL" =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
  echo "ERROR: Malformed PR URL. Expected: https://github.com/owner/repo/pull/123" >&2
  exit 1
fi

OWNER="${BASH_REMATCH[1]}"
REPO="${BASH_REMATCH[2]}"
PR_NUMBER="${BASH_REMATCH[3]}"

# ── Fetch PR metadata ────────────────────────────────────────────────────────

PR_META=$(gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      title
      state
      headRefName
      baseRefName
      body
      changedFiles
      additions
      deletions
      files(first: 100) {
        nodes { path additions deletions }
      }
    }
  }
}' -f owner="$OWNER" -f repo="$REPO" -F pr="$PR_NUMBER")

TITLE=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.title')
STATE=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.state')
HEAD_BRANCH=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.headRefName')
BASE_BRANCH=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.baseRefName')
BODY=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.body // ""')
CHANGED_FILES=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.changedFiles')
ADDITIONS=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.additions')
DELETIONS=$(echo "$PR_META" | jq -r '.data.repository.pullRequest.deletions')
FILES_JSON=$(echo "$PR_META" | jq -c '.data.repository.pullRequest.files.nodes')

# ── Detect repo path and language ─────────────────────────────────────────────

REPO_PATH="$SRC_ROOT/$REPO"
if [[ ! -d "$REPO_PATH" ]]; then
  echo "ERROR: Repo directory not found at $REPO_PATH" >&2
  exit 1
fi

if [[ -f "$REPO_PATH/go.mod" ]]; then
  LANG="go"
  BUILD_CMD="cd $REPO_PATH && go build ./..."
  LINT_CMD="cd $REPO_PATH && golangci-lint run --timeout=10m"
  TEST_CMD="cd $REPO_PATH && go test ./..."
  FMT_CMD="cd $REPO_PATH && gofmt -w ."
elif [[ -f "$REPO_PATH/turbo.json" ]]; then
  LANG="typescript (bun monorepo)"
  BUILD_CMD="cd $REPO_PATH && bunx turbo run check-types:dev --continue --concurrency=3"
  LINT_CMD="cd $REPO_PATH && bunx turbo run lint:fix format --continue --concurrency=3"
  TEST_CMD="cd $REPO_PATH && bunx turbo run test --continue --concurrency=3"
  FMT_CMD="cd $REPO_PATH && bunx turbo run format --continue --concurrency=3"
elif [[ -f "$REPO_PATH/package.json" ]]; then
  LANG="typescript"
  BUILD_CMD="cd $REPO_PATH && bun run build"
  LINT_CMD="cd $REPO_PATH && bun run lint"
  TEST_CMD="cd $REPO_PATH && bun test"
  FMT_CMD=""
elif [[ -f "$REPO_PATH/Cargo.toml" ]]; then
  LANG="rust"
  BUILD_CMD="cd $REPO_PATH && cargo build"
  LINT_CMD="cd $REPO_PATH && cargo clippy"
  TEST_CMD="cd $REPO_PATH && cargo test"
  FMT_CMD="cd $REPO_PATH && cargo fmt"
else
  LANG="unknown"
  BUILD_CMD=""
  LINT_CMD=""
  TEST_CMD=""
  FMT_CMD=""
fi

# ── Fetch unresolved review threads ──────────────────────────────────────────

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

# Shape threads: unresolved + not outdated, all comments preserved
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

FILE_GROUPS=$(echo "$THREADS" | jq '
  group_by(.path)
  | map({
      path: .[0].path,
      thread_count: length,
      threads: .
    })')

# ── Output structured context ────────────────────────────────────────────────

cat <<EOF
## PR Context

**URL:** $PR_URL
**Title:** $TITLE
**State:** $STATE
**Branch:** \`$HEAD_BRANCH\` → \`$BASE_BRANCH\`
**Changed files:** $CHANGED_FILES (+$ADDITIONS / -$DELETIONS)

## Repo

**Name:** $REPO
**Path:** $REPO_PATH
**Language:** $LANG
**Build:** \`$BUILD_CMD\`
**Lint:** \`$LINT_CMD\`
**Test:** \`$TEST_CMD\`
**Format:** \`$FMT_CMD\`

## PR Description

$BODY

## Changed Files

$(echo "$FILES_JSON" | jq -r '.[] | "- \(.path) (+\(.additions) / -\(.deletions))"')

## Unresolved Review Threads ($THREAD_COUNT total)

EOF

# Output each file group with its threads
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
