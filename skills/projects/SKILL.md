---
name: projects
description: >
  Track multi-milestone projects as a nested TODO list with a dependency graph.
  Use when the user types "/projects" to view the portfolio, create a project,
  or report progress.
argument-hint: <project-slug> <new|update> [details...]
disable-model-invocation: true
---

# Projects Skill

A nested TODO list with a dependency-graph visualization. This skill owns _what_ and _what's blocking_ — implementation happens outside.

## Context

!`~/.claude/skills/projects/scripts/projects-setup.sh "$0" "$1"`

Read the project file and AUDIT_LOG at the paths shown above to determine current state.

## Files

- **project.md** — live state: goal, plan (milestones + sessions as nested TODOs), dependency graph
- **AUDIT_LOG.md** — append-only history: every change with date + rationale

## Routing

| Invocation                           | Flow |
|--------------------------------------|------|
| `/projects`                          | Dashboard — list all projects from the script output. |
| `/projects <slug> new <description>` | Scaffold a new project. Start a conversation to align on goal, milestones, and sessions before writing anything. |
| `/projects <slug> update <...>`      | Any change on an existing project. Infer intent from the user's message (view, progress, completion, restructure). |

## Rules

- YYYY-MM-DD dates. Update `last_touched` on every doc change.
- Every change to project.md gets a dated AUDIT_LOG.md entry.
- Hyperlink external references: Linear as `[DEF-XXXXX](https://linear.app/...)`, GitHub as `[owner/repo#123](https://github.com/...)`, etc.
- Preserve the user's language.

## Scaffolding a New Project

The script creates an empty project.md template with format instructions as comments. **Do not fill it in right away.** Instead, have a conversation first:

1. **Understand the goal.** Read the user's description and ask questions about what they're actually trying to deliver, who it's for, and what success looks like. Don't assume — dig into the "why."
2. **Explore milestones together.** Propose rough milestones and ask the user to react — what's missing, what's wrong, what's the real priority order? Push back if something seems off.
3. **Break down sessions collaboratively.** Once milestones are agreed on, talk through what work each one involves. Ask about unknowns, risks, and dependencies the user sees.
4. **Only write project.md once aligned.** Read the template to understand the format, then fill it in based on the conversation. The plan should feel like something the user co-authored, not something generated at them.

## Completing a Session

1. Check the `[x]` box and append the ref (PR, ticket).
2. Remove the session from the dependency graph (node, edges, style).
3. Update blocker/blocking lines on all remaining sessions.
4. If all sessions in a milestone are done, check the milestone too.
5. Append to AUDIT_LOG.
6. Surface any newly-unblocked sessions.

## Completing a Milestone

All sessions must be done. Check the milestone box. If no milestones remain, ask if the project is `status: complete`.
