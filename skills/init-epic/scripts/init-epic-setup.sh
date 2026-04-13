#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ~/.dot-agent/skills/init-epic/scripts/init-epic-setup.sh \
    --workspace-title "Toolkit Rigby" \
    --focus "Rigby" \
    --repo "Toolkit.Web|https://example.com/Toolkit.Web|current|Current Rigby web app and host-side UI behavior." \
    --repo "Toolkit.API|https://example.com/Toolkit.API|current|Current Rigby backend and runtime support services." \
    --repo "workover-assistant|https://github.com/org/workover-assistant.git|legacy|Legacy Rigby reference implementation." \
    [--coord-role "cross-repo planning, project tracking, inventory notes, workflow docs, and coordination automation."] \
    [--init-git] \
    [--clone-missing] \
    [--force]

Notes:
  - Run from the coordination repo root you want to scaffold.
  - Repeat --repo once per imported repo.
  - Repo spec format is: name|url|current|role or name|url|legacy|role
  - Role text must not contain the "|" character.
  - --force overwrites AGENTS.md, README.md, and docs/inventory/*.md files.
  - .gitignore is managed idempotently through a dedicated block and is updated even without --force.
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_value() {
  local flag="$1"
  local value="${2:-}"
  [[ -n "$value" ]] || die "$flag requires a value"
}

slugify() {
  printf '%s' "$*" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g'
}

normalize_role() {
  printf '%s' "$1" | sed -E 's/[[:space:]]+$//; s/[.]$//'
}

markdown_link() {
  printf '[%s](%s)' "$1" "$2"
}

join_repo_links_by_kind() {
  local kind="$1"
  local idx
  local first=1

  for idx in "${!REPO_NAMES[@]}"; do
    [[ "${REPO_KINDS[$idx]}" == "$kind" ]] || continue
    if (( first == 0 )); then
      printf ', '
    fi
    markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}"
    first=0
  done
}

write_text_file() {
  local path="$1"
  local content="$2"

  if [[ -f "$path" && "$FORCE" -ne 1 ]]; then
    echo "SKIPPED_FILE=$path"
    return
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" >"$path"
  echo "WROTE_FILE=$path"
}

replace_gitignore_block() {
  local file=".gitignore"
  local tmp
  local block
  local idx

  block=$(
    {
      echo "# >>> init-epic managed block >>>"
      echo ".DS_Store"
      echo
      echo "# Local sibling clones used for cross-repo planning and implementation."
      for idx in "${!REPO_NAMES[@]}"; do
        printf '%s/\n' "${REPO_NAMES[$idx]}"
      done
      echo "# <<< init-epic managed block <<<"
    }
  )

  tmp="$(mktemp "${TMPDIR:-/tmp}/init-epic-gitignore.XXXXXX")"

  if [[ -f "$file" ]]; then
    awk '
      BEGIN { skip = 0 }
      /^# >>> init-epic managed block >>>$/ { skip = 1; next }
      /^# <<< init-epic managed block <<<$/{ skip = 0; next }
      skip == 0 { print }
    ' "$file" >"$tmp"

    if [[ -s "$tmp" ]]; then
      printf '\n' >>"$tmp"
    fi
  fi

  printf '%s\n' "$block" >>"$tmp"
  mv "$tmp" "$file"
  echo "WROTE_FILE=$file"
}

render_readme() {
  local idx

  echo "# $WORKSPACE_TITLE"
  echo
  echo "This repository is the coordination workspace for $FOCUS."
  echo
  echo "Production code changes belong in the upstream repo that owns the behavior. This repo should hold cross-repo plans, decision records, inventory notes, workflow clarifications, and coordination automation."
  echo
  echo "## Repo Roles"
  echo
  echo "| Repo | Type | Role |"
  echo "|---|---|---|"
  for idx in "${!REPO_NAMES[@]}"; do
    printf '| %s | %s | %s |\n' \
      "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")" \
      "${REPO_KINDS[$idx]}" \
      "${REPO_ROLES[$idx]}"
  done
  printf '| This repo | coordination | %s |\n' "$COORD_ROLE"
  echo
  echo "## Current vs Legacy"
  echo
  echo "Current implementation repos:"
  for idx in "${!REPO_NAMES[@]}"; do
    [[ "${REPO_KINDS[$idx]}" == "current" ]] || continue
    printf -- '- %s\n' "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")"
  done
  echo

  if (( LEGACY_COUNT > 0 )); then
    echo "Legacy reference repos:"
    for idx in "${!REPO_NAMES[@]}"; do
      [[ "${REPO_KINDS[$idx]}" == "legacy" ]] || continue
      printf -- '- %s\n' "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")"
    done
    echo
    echo "Use legacy repos to understand behavior, gaps, and migration sequencing rather than as the default place for new production work."
    echo
  fi

  echo "## Local Workspace"
  echo
  echo "Sibling clones live at the repo root and are intentionally gitignored so this workspace can be used for cross-repo planning and implementation without vendoring those repos into this coordination repo."
}

render_agents() {
  local idx
  local step=1

  echo "# $WORKSPACE_TITLE Instructions"
  echo
  echo "## Core Rules"
  echo "- Treat this repository as the coordination layer for $FOCUS work. Planning docs, workflow definitions, and cross-repo decisions belong here. Production implementation belongs in the upstream repo that owns the change."
  echo "- Treat repos marked \`current\` below as the current $FOCUS implementation. Treat repos marked \`legacy\` below as reference-only unless explicitly confirmed otherwise."
  echo "- Route every task to its owning repo before writing code."
  echo "- State the expected repo-to-repo dependency order whenever a task spans more than one repository."
  echo "- Do not invent build commands, package managers, or code conventions for an upstream repo that has not been inspected in the current session."
  echo
  echo "## Repo Map"
  for idx in "${!REPO_NAMES[@]}"; do
    printf -- '- %s: %s. %s\n' \
      "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")" \
      "${REPO_KINDS[$idx]}" \
      "${REPO_ROLES[$idx]}."
  done
  printf -- '- This repo: %s\n' "$COORD_ROLE"
  echo
  echo "## Task Routing"
  for idx in "${!REPO_NAMES[@]}"; do
    printf -- '- Route work to %s when the task belongs to this role: %s.\n' \
      "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")" \
      "${REPO_ROLES[$idx]}"
  done
  echo "- Route planning artifacts, dependency maps, migration notes, and coordination scripts to this repo."
  echo
  echo "## Coding Conventions"
  echo "- Keep documents here decision-oriented. Name the owning repo, whether the behavior is current or legacy, the dependency order, and any unresolved questions."
  echo "- Use YYYY-MM-DD dates in planning artifacts maintained from this repo."
  echo "- Add scripts only when they automate cross-repo coordination or validation, and document how to run them from the repo root."
  echo "- Prefer links to upstream repos, pull requests, and tickets over copied context."
  echo
  echo "## Workflow Expectations"
  echo "- Planning: decide whether the task is current implementation work, legacy reference work, or cross-repo alignment work before changing files."
  if (( LEGACY_COUNT > 0 )); then
    echo "- Discovery: inspect the legacy repos when you need prior behavior context, then confirm whether the same behavior still matters in the current repos before routing implementation."
  else
    echo "- Discovery: inspect the owning repos directly and record repo boundaries before starting cross-repo changes."
  fi
  echo "- Implementation: typical cross-repo work should follow this order:"
  if (( LEGACY_COUNT > 0 )); then
    printf '  %d. Confirm the relevant legacy behavior in %s when legacy context is needed.\n' \
      "$step" \
      "$(join_repo_links_by_kind legacy)"
    step=$((step + 1))
  fi
  for idx in "${!REPO_NAMES[@]}"; do
    [[ "${REPO_KINDS[$idx]}" == "current" ]] || continue
    printf '  %d. Prepare changes in %s when the slice belongs to this role: %s.\n' \
      "$step" \
      "$(markdown_link "${REPO_NAMES[$idx]}" "${REPO_URLS[$idx]}")" \
      "${REPO_ROLES[$idx]}"
    step=$((step + 1))
  done
  printf '  %d. Record dependency order, assumptions, and unresolved gaps here.\n' "$step"
  echo "- Review: summarize impacted repos, current versus legacy assumptions, rollout order, and any blockers another repo must clear."
  echo
  echo "## Conditional Guidance"
  echo
  echo "### Planning"
  echo "- If the request only affects this repo, keep it limited to docs, project state, templates, or coordination automation."
  echo "- If the request affects runtime behavior, identify the owning upstream repo before making changes."
  if (( LEGACY_COUNT > 0 )); then
    echo "- Use legacy repos to understand prior behavior, not as the default place for new production work."
  fi
  echo
  echo "### Implementation"
  echo "- Keep cross-repo assumptions written down here when another repo cannot be updated in the same session."
  echo "- When referencing sibling clones locally, use explicit filesystem paths in notes and commands."
  echo
  echo "### Review"
  echo "- Flag ownership leaks immediately: current implementation work in this repo or new production behavior added to a legacy repo without an explicit legacy-only reason."
  echo "- Verify that the merge and release order is clear whenever multiple repos change."
  echo
  echo "## Anti-Patterns"
  echo "- Using this repo as the place for production application code instead of coordination artifacts."
  if (( LEGACY_COUNT > 0 )); then
    echo "- Treating legacy repos as the current owner by default."
  fi
  echo "- Porting legacy behavior without first confirming that the behavior still matters and which current repo owns it."
  echo "- Letting repo-boundary decisions live only in chat instead of capturing them here."
}

render_inventory() {
  local idx="$1"
  local name="${REPO_NAMES[$idx]}"
  local url="${REPO_URLS[$idx]}"
  local kind="${REPO_KINDS[$idx]}"
  local role="${REPO_ROLES[$idx]}"
  local title_suffix="Inventory"

  if [[ "$kind" == "legacy" ]]; then
    title_suffix="Legacy Inventory"
  fi

  echo "# $name - $FOCUS $title_suffix"
  echo
  echo "**Snapshot date:** $TODAY"
  echo "**Repo:** $(markdown_link "$name" "$url")"
  echo "**Local clone:** \`./$name\`"
  echo
  echo "## Role"
  echo
  echo "$role"
  echo
  echo "## What To Capture"
  echo

  if [[ "$kind" == "current" ]]; then
    echo "- Entry points, modules, or flows that implement current $FOCUS behavior"
    echo "- Integration points with the other repos in this workspace"
    if (( LEGACY_COUNT > 0 )); then
      echo "- Any places where the legacy reference repos still need parity, migration, or intentional divergence"
    else
      echo "- Open coordination dependencies that affect this repo"
    fi
  else
    echo "- Legacy $FOCUS behaviors worth preserving, intentionally dropping, or translating"
    echo "- Contracts, assumptions, or runtime expectations that still matter to the current implementation repos"
    echo "- Gaps between this repo and the current implementation repos in this workspace"
  fi

  echo
  echo "## Notes"
  echo
  if [[ "$kind" == "current" ]]; then
    echo "Populate during the initial current-state inventory session."
  else
    echo "Populate during the initial legacy inventory session."
  fi
}

WORKSPACE_TITLE=""
FOCUS=""
COORD_ROLE="cross-repo planning, project tracking, inventory notes, workflow docs, and coordination automation."
INIT_GIT=0
CLONE_MISSING=0
FORCE=0
TODAY="$(date +%Y-%m-%d)"

declare -a REPO_SPECS
declare -a REPO_NAMES
declare -a REPO_URLS
declare -a REPO_KINDS
declare -a REPO_ROLES
declare -a REPO_FILES

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace-title)
      require_value "$1" "${2:-}"
      WORKSPACE_TITLE="$2"
      shift 2
      ;;
    --focus)
      require_value "$1" "${2:-}"
      FOCUS="$2"
      shift 2
      ;;
    --repo)
      require_value "$1" "${2:-}"
      REPO_SPECS+=("$2")
      shift 2
      ;;
    --coord-role)
      require_value "$1" "${2:-}"
      COORD_ROLE="$2"
      shift 2
      ;;
    --init-git)
      INIT_GIT=1
      shift
      ;;
    --clone-missing)
      CLONE_MISSING=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

[[ -n "$WORKSPACE_TITLE" ]] || die "--workspace-title is required"
[[ -n "$FOCUS" ]] || die "--focus is required"
(( ${#REPO_SPECS[@]} > 0 )) || die "At least one --repo entry is required"

CURRENT_COUNT=0
LEGACY_COUNT=0

for spec in "${REPO_SPECS[@]}"; do
  IFS='|' read -r name url kind role extra <<<"$spec"

  [[ -n "$name" ]] || die "Repo spec is missing name: $spec"
  [[ -n "$url" ]] || die "Repo spec is missing url: $spec"
  [[ -n "$kind" ]] || die "Repo spec is missing kind: $spec"
  [[ -n "$role" ]] || die "Repo spec is missing role: $spec"
  [[ -z "${extra:-}" ]] || die "Repo spec has too many fields: $spec"
  [[ "$name" != */* ]] || die "Repo name must be a single directory name: $name"

  case "$kind" in
    current)
      CURRENT_COUNT=$((CURRENT_COUNT + 1))
      ;;
    legacy)
      LEGACY_COUNT=$((LEGACY_COUNT + 1))
      ;;
    *)
      die "Repo kind must be current or legacy: $spec"
      ;;
  esac

  REPO_NAMES+=("$name")
  REPO_URLS+=("$url")
  REPO_KINDS+=("$kind")
  REPO_ROLES+=("$(normalize_role "$role")")
  REPO_FILES+=("$(slugify "$name").md")
done

(( CURRENT_COUNT > 0 )) || die "At least one current repo is required"

echo "WORKSPACE_ROOT=$PWD"
echo "WORKSPACE_TITLE=$WORKSPACE_TITLE"
echo "FOCUS=$FOCUS"
echo "CURRENT_REPOS=$(join_repo_links_by_kind current)"
if (( LEGACY_COUNT > 0 )); then
  echo "LEGACY_REPOS=$(join_repo_links_by_kind legacy)"
fi

mkdir -p docs/inventory

replace_gitignore_block
write_text_file "README.md" "$(render_readme)"
write_text_file "AGENTS.md" "$(render_agents)"

for idx in "${!REPO_NAMES[@]}"; do
  write_text_file "docs/inventory/${REPO_FILES[$idx]}" "$(render_inventory "$idx")"
done

if (( INIT_GIT == 1 )); then
  if [[ -d .git ]]; then
    echo "SKIPPED_GIT_INIT=1"
  else
    if git init -b main >/dev/null 2>&1; then
      :
    else
      git init >/dev/null
    fi
    echo "INITIALIZED_GIT=1"
  fi
fi

CLONE_ERRORS=0
if (( CLONE_MISSING == 1 )); then
  for idx in "${!REPO_NAMES[@]}"; do
    repo_name="${REPO_NAMES[$idx]}"
    repo_url="${REPO_URLS[$idx]}"

    if [[ -d "$repo_name/.git" ]]; then
      echo "SKIPPED_CLONE=$repo_name"
      continue
    fi

    if [[ -e "$repo_name" ]]; then
      echo "WARN: $repo_name exists but is not a git repo; skipping clone" >&2
      CLONE_ERRORS=1
      continue
    fi

    if git clone "$repo_url" "$repo_name"; then
      echo "CLONED_REPO=$repo_name"
    else
      echo "WARN: Failed to clone $repo_name from $repo_url" >&2
      CLONE_ERRORS=1
    fi
  done
fi

echo "NEXT_STEP=Use the projects skill if this workspace needs milestone and session tracking."

exit "$CLONE_ERRORS"
