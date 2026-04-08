---
name: cmux
description: Fan out a skill across multiple todos in separate cmux workspaces. Usage: /cmux <skill> <todo-id> [todo-id...]
disable-model-invocation: true
---

# /cmux

Open a new cmux workspace (tab) for each specified todo, running the given skill in each.

## Usage

```
/cmux <skill> <todo-id> [todo-id...]
```

**Example:** `/cmux /spec-new-feature 58 59 60`

## Instructions

1. **Parse arguments.** The first argument is the skill/command to run. Remaining arguments are todo IDs (integers).
2. **Resolve todos.** Read `data/todos.csv` and look up each ID. Extract the `item` text for each.
3. **Create worktrees and launch workspaces.** For each todo:
   a. Create a git worktree on a new branch:
   ```bash
   git worktree add /tmp/cmux-todo-<id> -b cmux/todo-<id>
   ```
   b. Launch a cmux workspace in that worktree:
   ```bash
   cmux new-workspace --cwd /tmp/cmux-todo-<id> --command "claude --dangerously-skip-permissions '<skill> on todo #<id>: <item>'"
   ```
4. **Report.** List each workspace created with its todo ID, branch name, and worktree path.

## Rules

- If a todo ID is not found in todos.csv, skip it and warn the user.
- If no valid todo IDs are provided, stop and tell the user.
- Launch all workspaces — do not ask for confirmation.
- Keep the prompt passed to claude concise: just the skill invocation and the todo context.
