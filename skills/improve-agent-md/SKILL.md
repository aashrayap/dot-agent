---
name: improve-agent-md
description: Rewrite a primary agent instruction file such as CLAUDE.md or AGENTS.md so the always-on guidance stays short and task-specific rules are easier for the agent to follow. Use Claude-style <important if> blocks only for Claude targets; use explicit conditional sections for Codex targets.
argument-hint: [path-to-agent-md]
disable-model-invocation: true
---

# Improve Agent Markdown

Use this when the user wants to tighten an existing agent instruction file instead of creating a brand-new one.

## Target Selection

Default in this order:

1. user-provided path
2. `./CLAUDE.md`
3. `./AGENTS.md`
4. `~/.claude/CLAUDE.md`
5. `~/.codex/AGENTS.md`

If both repo-local files exist and the user did not name a target, prefer the file for the current runtime. If the intent is still ambiguous, ask one short question.

If the user asks to improve both paired runtime files in one repo, update both and keep the factual content aligned, but do not force the same structure across runtimes.

## Shared Goal

Rewrite the file so that:

- always-on context is genuinely always relevant
- task-specific guidance is separated cleanly
- stale snippets, vague policy text, and linter territory are removed
- commands, repo map, and verification expectations survive when they are still accurate

Patch the file in place unless the user explicitly asks for a draft in chat.

## Shared Rewrite Rules

- Keep project identity, repo map, tech stack, and other onboarding context near the top.
- Preserve useful command references. Do not silently drop commands just because they are infrequent.
- Remove style rules that should live in linters, formatters, typecheckers, or pre-commit hooks.
- Remove vague instructions such as "follow best practices" unless you can replace them with a concrete operational rule.
- Replace stale code snippets with file path references when a live example already exists in the repo.
- Split broad mixed sections into narrow, task-shaped guidance.
- Prefer short bullets over long prose blocks.
- Keep the result concise. If a rule is obvious from repo structure or consistent code patterns, cut it.

## Claude Targets

When the target file is `CLAUDE.md`, use Claude-native conditional weighting with `<important if="...">` blocks.

### Claude Rules

- Keep project identity, directory map, and high-level stack details as bare markdown at the top.
- Put command references in one targeted block, usually for building, testing, linting, generating, or deploying.
- Use narrow trigger conditions. "you are writing code" is too broad; "you are writing or modifying tests" is appropriate.
- Do not wrap everything. Foundational context should remain outside conditional blocks.
- Keep each block internally coherent. Do not mix testing, API, and deployment rules inside one condition.

### Claude Skeleton

```markdown
# CLAUDE.md

[one-line project identity]

## Project map
- `apps/api/` - ...
- `apps/web/` - ...

<important if="you need to run build, test, lint, or code generation commands">
[commands]
</important>

<important if="you are writing or modifying tests">
- [test guidance]
</important>

<important if="you are adding or modifying API routes">
- [API guidance]
</important>
```

Use `<important if>` only where the condition helps Claude decide relevance.

## Codex Targets

When the target file is `AGENTS.md`, do not lean on Claude-specific XML weighting. Rewrite it as a short always-on core plus explicit conditional sections with clear headings.

### Codex Rules

- Keep the top section limited to rules that should apply almost every turn.
- Group conditional guidance by activity: planning, implementation, testing, review, deployment, and similar work modes.
- Favor operational rules that change behavior over philosophy statements.
- Remove Claude-only syntax, tool assumptions, or slash-command wording unless the file is intentionally shared across runtimes.
- Preserve verification commands, file references, and reporting expectations.

### Codex Skeleton

```markdown
# Global Instructions

## Core Rules
- [short always-on rule]
- [short always-on rule]

## Workflow Expectations
- [planning expectation]
- [implementation expectation]
- [review expectation]

## Conditional Guidance

### Planning
- [what to do before major changes]

### Implementation
- [how to keep edits scoped and verifiable]

### Testing
- [when and how to verify]

### Review
- [how to report findings]

## Anti-Patterns
- [thing to avoid]
```

## Cross-Runtime Migration

When translating the same source material across both runtimes:

- keep the facts aligned
- keep commands and repo paths aligned
- translate structure, not wording
- use `<important if>` blocks only in Claude-facing files
- use headed conditional sections in Codex-facing files

## Final Checks

Before you finish:

- verify the commands still exist
- verify the referenced paths still exist
- remove contradictory runtime-specific instructions
- make sure conditions are narrow and actionable
- make sure the file got shorter or sharper, not broader
