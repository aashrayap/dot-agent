#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "ERROR: Usage: scripts/init-feature-artifacts.sh <feature-slug-or-title>"
  exit 1
fi

slugify() {
  printf '%s' "$*" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g'
}

status_of() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "missing"
    return
  fi

  awk -F': *' '/^status:/ { print $2; exit }' "$path"
}

FEATURE_SLUG="$(slugify "$*")"

if [[ -z "$FEATURE_SLUG" ]]; then
  echo "ERROR: Could not derive a valid feature slug from: $*"
  exit 1
fi

FEATURE_DIR="docs/artifacts/$FEATURE_SLUG"
SPEC_FILE="$FEATURE_DIR/01_spec.md"
QUESTIONS_FILE="$FEATURE_DIR/02_questions.md"
RESEARCH_FILE="$FEATURE_DIR/03_research.md"
DESIGN_FILE="$FEATURE_DIR/04_design.md"
TASKS_FILE="$FEATURE_DIR/05_tasks.md"

if [[ -d "$FEATURE_DIR" ]]; then
  MODE="resume"
else
  MODE="new"
  mkdir -p "$FEATURE_DIR"

  cat >"$SPEC_FILE" <<EOF
---
status: draft
feature: $FEATURE_SLUG
---

# Feature Spec: $FEATURE_SLUG

## Goal

## Users and Workflows

## Acceptance Criteria

## Boundaries

## Risks and Dependencies
EOF

  cat >"$QUESTIONS_FILE" <<EOF
---
status: pending
feature: $FEATURE_SLUG
---

# Research Questions: $FEATURE_SLUG

## Codebase

## Docs

## Patterns

## External
EOF

  cat >"$RESEARCH_FILE" <<EOF
---
status: pending
feature: $FEATURE_SLUG
---

# Research: $FEATURE_SLUG

## Findings
EOF

  cat >"$DESIGN_FILE" <<EOF
---
status: pending
feature: $FEATURE_SLUG
---

# Design: $FEATURE_SLUG

## Decisions
EOF

  cat >"$TASKS_FILE" <<EOF
---
status: pending
feature: $FEATURE_SLUG
---

# Tasks: $FEATURE_SLUG

## Task List
EOF
fi

printf 'MODE=%s\n' "$MODE"
printf 'FEATURE_SLUG=%s\n' "$FEATURE_SLUG"
printf 'FEATURE_DIR=%s\n' "$FEATURE_DIR"
printf 'SPEC_STATUS=%s\n' "$(status_of "$SPEC_FILE")"
printf 'QUESTIONS_STATUS=%s\n' "$(status_of "$QUESTIONS_FILE")"
printf 'RESEARCH_STATUS=%s\n' "$(status_of "$RESEARCH_FILE")"
printf 'DESIGN_STATUS=%s\n' "$(status_of "$DESIGN_FILE")"
printf 'TASKS_STATUS=%s\n' "$(status_of "$TASKS_FILE")"
