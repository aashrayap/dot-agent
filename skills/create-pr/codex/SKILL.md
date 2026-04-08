---
name: create-pr
description: Commit, review, push, and open a pull request — all-in-one. Use when finishing work on a branch and ready to create a PR. Handles ADO and GitHub remotes, conventional commits, lint/test gates, code review, and PR description generation.
---

# Create PR

End-to-end flow: issue → commit → lint/test → code review → push → create PR.

## Steps

### 1. Gather Context

- `git status`
- `git diff HEAD`
- `git branch --show-current`
- `git remote -v`

### 2. What Problem Are We Solving?

Ask the user for the source:

1. **ADO work item ID** (e.g., `12345`)
2. **GitHub issue** (number or URL)
3. **Free text** — user describes it directly

Based on the answer:

- **ADO work item** → fetch via `az boards work-item show --id {id}` — pull title, description, acceptance criteria
- **GitHub issue** → fetch via `gh issue view {number}` — pull title, body, labels
- **Free text** → user describes the problem/requirement directly

This is the **source of truth** for branch naming, commit messages, PR description, and work item linking.

### 3. Detect Platform

Inspect git remote URL:

- Contains `dev.azure.com` or `visualstudio.com` → **ADO** (use `az repos` CLI)
- Contains `github.com` → **GitHub** (use `gh` CLI)
- Otherwise → ask user

### 4. Resolve Target Branch

- `develop` exists? → target `develop`
- No `develop`, `main` exists? → target `main`
- Neither → ask user

Check via `git ls-remote --heads origin develop` and `git ls-remote --heads origin main`.

### 5. Branch Handling

- **On main/develop?** → Auto-create branch:
  - `feature/{workItemId}-{description}` for new functionality
  - `fix/{workItemId}-{description}` for bug fixes
- **On feature/fix branch?** → Continue
- **Unrecognized pattern?** → Ask user

### 6. Commit

- **Dirty tree?** → Stage all, generate conventional commit (`feat:`, `fix:`, etc.), commit
- **Clean tree?** → Skip
- Reference the issue (`AB#{id}` for ADO, `#{number}` for GitHub)

### 7. Validate Lint & Tests

Run project's lint and test commands. Both must pass before proceeding. If either fails, stop and show failures.

### 8. Code Review

Pre-push review. Run locally before PR creation.

#### 8a. Gather guidelines

Collect AGENTS.md / CLAUDE.md files from repo root and affected directories.

#### 8b. Review the changes

Review the diff for:
1. **Guidelines compliance** — audit against project guidelines
2. **Bug scan** — shallow scan for obvious bugs in the diff only; ignore pre-existing issues
3. **Code comment compliance** — verify changes comply with guidance in code comments

#### 8c. Confidence scoring

Score each issue 0–100:

| Score | Meaning |
|-------|---------|
| 0 | False positive |
| 25 | Might be real |
| 50 | Real but minor |
| 75 | Verified real, important |
| 100 | Confirmed, evidence-backed |

**Ignore:** pre-existing issues, linter-catchable issues, pedantic nitpicks, issues silenced by lint ignore comments.

#### 8d. Filter and fix

- Filter issues >= 75
- If found: show to user, fix, amend commit, re-run lint/test
- If none >= 75 → continue

### 9. Push

Push with `-u` to set upstream tracking.

### 10. Detect PR Format

- `feature/*` → Story format
- `fix/*` → Bug fix format
- Other → Ask user

### 11. Analyze Changes

Compare against target branch. Categorize diff into logical groups.

### 12. Generate PR Description

#### Story Format (feature/*)

```
## Summary
{1-2 sentences — what problem this solves}

## {Category}
{Bullets}

## Stats
{N} files | +{adds} / -{deletes} lines
```

#### Bug Fix Format (fix/*)

```
## Summary
{1-2 sentences — what was broken}

## Bug Fixes

| ID | Title | Fix |
|---|---|---|
| {id} | {title} | {1-line description} |

## Files Changed
{Grouped by area}
```

### 13. Create the PR

**ADO:**
```bash
az repos pr create --source-branch {branch} --target-branch {target} --title "{title}" --description "{body}" --work-items {ids}
```

**GitHub:**
```bash
gh pr create --base {target} --head {branch} --title "{title}" --body "{body}"
```

## Rules

- **No AI attribution** — no "Generated with Claude/Codex", no co-author lines, no emojis, no AI links
- No emoji in PR descriptions
- Target branch: `develop` > `main` > ask
- Summary: 1-2 sentences max, framed around the problem being solved
- Stats format: `{N} files | +{adds} / -{deletes} lines`
- Commits: conventional format (`feat:`, `fix:`, etc.)
- Never force-push shared branches (`develop`, `main`, `release/*`)
