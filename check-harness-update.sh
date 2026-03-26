#!/bin/bash
# Check if ~/.claude harness repo has upstream updates.
# Runs once per session (5-min cooldown via timestamp file).
# Called by PreToolUse hook — output goes into conversation.

REPO="$HOME/.claude"
STAMP="$REPO/.last-update-check"
COOLDOWN=300 # seconds

# Not a git repo → exit silently
[ -d "$REPO/.git" ] || exit 0

# Already checked recently → exit silently
if [ -f "$STAMP" ]; then
    LAST=$(stat -f %m "$STAMP" 2>/dev/null || stat -c %Y "$STAMP" 2>/dev/null)
    NOW=$(date +%s)
    [ $(( NOW - LAST )) -lt $COOLDOWN ] && exit 0
fi

# Fetch and check
cd "$REPO"
git fetch --quiet 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)

touch "$STAMP"

if [ -n "$BEHIND" ] && [ "$BEHIND" -gt 0 ]; then
    echo "⚠ Harness has $BEHIND update(s). Run: cd ~/.claude && git pull"
fi
