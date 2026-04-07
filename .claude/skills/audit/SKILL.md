---
name: audit
description: Codebase health scan. Finds dead files, stale docs, orphaned code, and doc drift. Read-only — identifies but never deletes.
---

# Audit

Read-only codebase health scan. Outputs findings to conversation + versioned report.

## Triggers

- `audit`, `audit codebase`, `codebase audit`
- `find dead code`, `cleanup scan`, `what's stale`

## Output

1. Concise summary in conversation
2. Versioned report written to `docs/audits/YYYY-MM-DD.md`

Reports must be concise (<80 lines). Capture findings only, not explanations.

## Scan Protocol

Scan each layer bottom-up. For each layer, check references bidirectionally (does the thing reference valid targets? is the thing referenced by anything?).

### L0: Core Docs

Files: `CLAUDE.md`, `docs/*.md`, `.claude/skills/*/SKILL.md`, `.claude/prompts/*.md`, memory `MEMORY.md`

Checks:
- Do file paths referenced in docs still exist?
- Do data schemas in docs match actual data files?
- Do routes/pages listed in docs match actual source files?
- Do skills listed in `CLAUDE.md` match actual skill directories?
- Are there shipped specs in `docs/specs/` that should be archived or deleted?
- Does `MEMORY.md` contain claims that contradict current code?

### L1: Core Data

Files: data files (CSV, JSON, etc.) in the project's data directory

Checks:
- Is every data file referenced by at least one route, lib function, or script?
- Do data file schemas match what docs describe?
- Are there data files not listed in the project's CLAUDE.md?

### L2: Intelligence

Files: library/utility modules, API routes, backend logic

Checks:
- Is every lib file imported by at least one consumer?
- Is every API route called by at least one page or skill?
- Are there exports that nothing imports?

### L3: Surfaces

Files: pages, components, UI entry points

Checks:
- Is every component imported by at least one page?
- Are there pages not linked in navigation?
- Are there redirect-only pages that could be removed?

## Report Format

```markdown
# Audit YYYY-MM-DD

## Summary
- X findings across Y layers
- HIGH: N | MEDIUM: N | LOW: N

## L0: Core Docs
| Finding | Confidence | Detail |
|---------|-----------|--------|

## L1: Core Data
| Finding | Confidence | Detail |
|---------|-----------|--------|

## L2: Intelligence
| Finding | Confidence | Detail |
|---------|-----------|--------|

## L3: Surfaces
| Finding | Confidence | Detail |
|---------|-----------|--------|

## Recommended Actions
- [numbered list, most impactful first]
```

## Confidence Levels

- **HIGH**: Zero references in code. Safe to remove.
- **MEDIUM**: Low references or flagged for removal in prior decisions. Verify before acting.
- **LOW**: Possible drift or minor inconsistency. Note for awareness.

## Rules

- Read-only. Never delete, edit, or create files (except the audit report).
- Use `Glob` and `Grep` tools, not shell commands, for file discovery.
- Cross-reference bidirectionally: check both "is this used?" and "does this reference valid things?"
- Skip files that are obviously active (e.g., page files linked in nav with live API calls).
- Compare against previous audits in `docs/audits/` to note recurring findings or resolved items.
- Keep the report under 80 lines. If more findings exist, prioritize HIGH confidence.
