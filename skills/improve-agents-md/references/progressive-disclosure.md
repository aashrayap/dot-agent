# Progressive Disclosure For Agent Instructions

Use this reference when rewriting long `AGENTS.md` or `CLAUDE.md` files, aligning
paired Claude/Codex files, or converting setup-heavy instructions into a lean
operating contract.

Default posture: improve an existing instruction file first. Create from a
template only when no useful file exists or the current file is beyond salvage.

Reference pattern: HumanLayer's March 17, 2026 note on CLAUDE.md adherence
recommends keeping foundational content visible while moving task-specific
Claude guidance into narrow `<important if="...">` blocks:
https://www.humanlayer.dev/blog/stop-claude-from-ignoring-your-claude-md

## Classification Pass

Classify every section before editing:

- Always-on: project identity, instruction precedence, human response contract,
  core work loop, critical safety, and common verification expectations.
- Conditional: testing, deployment, release, review, planning, migrations, skill
  authoring, setup, generated assets, and rarely used workflows.
- Referenced: repo shape details, long command lists, schemas, setup contracts,
  examples, troubleshooting, diagrams, and historical rationale.
- Deleted: stale snippets, duplicated facts, vague preferences, linter rules,
  and content contradicted by current repo reality.

If the target file lacks a concrete Human Response Contract, establish one
explicitly. Keep the required packet slots visible near the top instead of
leaving them implied.

## Codex `AGENTS.md`

- Keep the file readable as plain Markdown.
- Keep the Human Response Contract near the top and always visible.
- Use "Read When Needed" links for deeper contracts.
- Use headed conditional sections instead of Claude XML.
- Keep paths concrete and relative when repo-local.
- Do not hide critical safety or response-contract requirements in references.

Good Codex section names:

- `Operating Loop`
- `Planning`
- `Coding`
- `Review`
- `Progressive Disclosure`
- `Read When Needed`
- `Anti-Patterns`

## Claude `CLAUDE.md`

- Keep foundational content always visible when it applies to most tasks.
- Keep the Human Response Contract always visible near the top; do not wrap it
  in `<important if="...">`.
- Use `<important if="...">` only for narrow task conditions.
- Make conditions specific enough that they should fire only for the intended
  work path.
- Prefer pulling test, release, setup, and authoring rules out of long always-on
  prose and into narrow conditional blocks.
- Keep Claude-only XML out of `AGENTS.md`.

Good Claude conditions:

```xml
<important if="you are writing or modifying tests">
...
</important>

<important if="you are changing deployment, release, or setup scripts">
...
</important>

<important if="you are creating or materially rewriting a skill">
...
</important>
```

Avoid conditions like `you are writing code`; they are too broad to improve
relevance.

## Skill Instructions

When rewriting skill instructions:

- Preserve the `## Composes With` section near the top.
- Keep the skill root focused on trigger, composition, and core workflow.
- Move domain references into `references/`.
- Move deterministic helpers into `scripts/`.
- Move output templates into `assets/`.
- Move runtime-neutral support files into `shared/`.
- Use thin `claude/` or `codex/` wrappers only when runtime syntax differs.

## Review Checklist

- Always-on content now describes how the agent should operate, not every fact
  it might someday need.
- Conditional sections are narrow and actionable.
- Referenced files have clear "read when" guidance from the entrypoint.
- Facts stay aligned across Claude and Codex files.
- Referenced commands and paths exist.
- The rewrite preserved crucial composition, setup, and verification contracts.
