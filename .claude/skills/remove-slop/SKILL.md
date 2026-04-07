---
name: remove-slop
description: Check the diff against main and remove all AI-generated slop introduced in this branch.
---

# Remove Slop

Post-edit quality gate. Diffs against main and strips AI-generated code patterns that don't match the codebase style.

## Triggers

- `remove slop`, `clean up slop`, `slop check`
- Run automatically as part of Phase 4 (Verify) in the feature pipeline

## What Counts as Slop

1. **Extra comments** a human wouldn't add, or that are inconsistent with the rest of the file
2. **Defensive overkill** — try/catch blocks, null checks, or guards that are abnormal for that area of the codebase (especially when called by trusted/validated codepaths)
3. **Casts to `any`** used to sidestep type issues instead of fixing them
4. **Style inconsistencies** — naming, spacing, patterns that don't match the surrounding file
5. **Unnecessary abstractions** — helpers, wrappers, or indirection added for a single use
6. **Verbose error handling** where the codebase convention is to let errors propagate

## Protocol

1. Get the diff:
   ```bash
   git diff main -- '*.ts' '*.tsx'
   ```
   If on main with uncommitted changes, use `git diff` instead.

2. For each changed file in the diff:
   - Read the full file (not just the diff) to understand surrounding style
   - Identify any hunks that match the slop patterns above
   - Fix in place: remove the slop, match the file's existing conventions

3. After all fixes, run the project's build command to confirm nothing broke.

4. Report a summary:
   ```
   SLOP REMOVED
   ├─ file.ts: removed 2 unnecessary try/catch blocks
   ├─ component.tsx: removed 3 redundant comments
   └─ lib.ts: replaced `as any` with proper type
   ```
   If no slop found, report "Clean — no slop detected."

## Rules

- Only touch files in the current diff. Never modify unrelated files.
- Match the existing file's style — don't impose a new one.
- When in doubt whether something is slop, leave it. False negatives are better than breaking code.
- Always build-verify after changes.
