#!/usr/bin/env bash
set -euo pipefail

# Usage: new-feature-setup.sh <kebab-name>
# Creates docs/<name>/ with template files if it doesn't exist,
# or reports current status for resumption.

if [[ $# -lt 1 ]]; then
  echo "ERROR: Usage: /spec-new-feature <kebab-name>"
  echo "Example: /spec-new-feature test-website"
  exit 1
fi

NAME="$1"
TODAY=$(date +%Y-%m-%d)

# Validate kebab-case
if [[ ! "$NAME" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: '$NAME' is not valid kebab-case."
  echo "Must be lowercase letters/digits/hyphens, start with a letter, no leading/trailing/consecutive hyphens."
  exit 1
fi

# Require at least one hyphen (single word likely means user forgot the name)
if [[ "$NAME" != *-* ]]; then
  echo "ERROR: '$NAME' must contain at least one hyphen (e.g. 'my-feature')."
  echo "A single word likely means you forgot to set a name."
  echo "Usage: /spec-new-feature <kebab-name>"
  exit 1
fi

# Resume if a directory matching *-<name> already exists
EXISTING_DIR=$(find docs -maxdepth 1 -type d -name "*-${NAME}" 2>/dev/null | head -1)
if [[ -n "$EXISTING_DIR" ]]; then
  DIR="$EXISTING_DIR"
  echo "FEATURE_DIR=$DIR"
  echo "FEATURE_NAME=$NAME"
  echo "MODE=resume"
  echo ""
  echo "Current status:"
  for f in 01_spec.md 02_questions.md 03_findings.md 04_plan.md 05_tasks.md; do
    if [[ -f "$DIR/$f" ]]; then
      status=$(head -5 "$DIR/$f" | grep -m1 'status:' | sed 's/.*status: *//' || echo "unknown")
      echo "  ${f}: ${status}"
    fi
  done
  exit 0
fi

# Create directory with unix timestamp (ms) prefix for chronological sorting
TIMESTAMP_MS=$(($(date +%s) * 1000))
DIR="docs/${TIMESTAMP_MS}-${NAME}"
mkdir -p "$DIR"

cat > "$DIR/01_spec.md" << EOF
---
status: draft
feature: $NAME
created: $TODAY
---

# Feature: $NAME

## Brief
- **What:**
- **Why:**
- **Who:**
- **Success:**
- **Constraints:**

## User Stories

### Story 1: [Title]
**As a** [user type] **I want to** [action] **so that** [outcome]

**Acceptance Criteria:**
- [ ] Given [precondition], when [action], then [result]
- [ ] Edge case: Given [unusual condition], then [handling]

## Risks

### Known-Unknowns
-

### Assumptions
-

### Dependencies
-

## Boundaries

### Out of Scope
-

### Must Not
-

### Error Handling
-
EOF

cat > "$DIR/02_questions.md" << EOF
---
status: pending
feature: $NAME
created: $TODAY
---

# Investigation Questions

## Codebase Questions

## External Questions

## Convention Questions
EOF

cat > "$DIR/03_findings.md" << EOF
---
status: pending
feature: $NAME
created: $TODAY
---

# Investigation Findings: $NAME

## Codebase Findings

### Existing Capabilities

### Data Layer

### Conventions and Patterns

## External Findings

## Surprise Discoveries

## Unresolved
EOF

cat > "$DIR/04_plan.md" << EOF
---
status: pending
feature: $NAME
created: $TODAY
---

# Technical Plan: $NAME

## Relevant Principles

## Decisions

## Technical Design

**Approach:**

**Data model changes:**

**API contracts:**

**Integration points:**

**File-level change map:**

| File | Action | Description |
|------|--------|-------------|
EOF

cat > "$DIR/05_tasks.md" << EOF
---
status: pending
feature: $NAME
created: $TODAY
---

# Tasks: $NAME

## Execution Order
EOF

echo "FEATURE_DIR=$DIR"
echo "FEATURE_NAME=$NAME"
echo "MODE=new"
echo ""
echo "Created $DIR/"
echo "  01_spec.md      (draft)"
echo "  02_questions.md (pending)"
echo "  03_findings.md  (pending)"
echo "  04_plan.md      (pending)"
echo "  05_tasks.md     (pending)"
