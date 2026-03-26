---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(git push:*), Bash(git branch:*), Bash(git log:*)
description: Stage all changes, commit with a good message, and push
---

Stage all changes, generate a conventional commit message from the diff, commit, and push to the current branch.

1. Run `git status` and `git diff --staged` to understand what's being committed.
2. If nothing is staged, stage all modified/added files (but warn about untracked files).
3. Generate a commit message: `type(scope): description` format.
4. Commit and push to the current branch.
5. Report the commit hash and branch.
