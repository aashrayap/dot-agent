#!/bin/bash
# Check if the canonical dot-agent repo has upstream updates.
# Runs once per session with a short cooldown via a stamp file.

set -euo pipefail

REPO="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
STAMP="$HOME/.claude/.last-update-check"
COOLDOWN=300

[ -d "$REPO/.git" ] || exit 0

if [ -f "$STAMP" ]; then
  LAST=$(stat -f %m "$STAMP" 2>/dev/null || stat -c %Y "$STAMP" 2>/dev/null)
  NOW=$(date +%s)
  [ $(( NOW - LAST )) -lt $COOLDOWN ] && exit 0
fi

cd "$REPO"
git fetch --quiet 2>/dev/null || exit 0
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)

touch "$STAMP"

if [ -n "$BEHIND" ] && [ "$BEHIND" -gt 0 ]; then
  echo "⚠ dot-agent has $BEHIND update(s). Run: cd ~/.dot-agent && git pull"
fi
