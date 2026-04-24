---
name: ubiquitous-language
description: Generate, refresh, locate, or lint a repo-level `docs/UBIQUITOUS_LANGUAGE.md` shared terminology artifact. Use when the user asks for ubiquitous language, shared language, terminology alignment, domain vocabulary, glossary-like repo terms, or implementation alignment between docs, code, planning, and review.
---

# Ubiquitous Language

## Composes With

- Parent: user request to create, refresh, locate, or lint repo terminology.
- Children: `spec-new-feature` when shared language feeds feature planning; `review` when terminology drift should be checked; `improve-agents-md` when instruction surfaces need follow-up alignment.
- Uses format from: existing repo doc contracts and `docs/UBIQUITOUS_LANGUAGE.md` table schema.
- Reads state from: active repo docs, `AGENTS.md`, `README.md`, domain schemas, existing `docs/UBIQUITOUS_LANGUAGE.md`, and helper inventory output.
- Writes through: `scripts/ubiquitous-language.py` for scaffold, locate, inventory, lint, and optional `AGENTS.md` pointer injection.
- Hands off to: `spec-new-feature` for code-grounded planning and `review` for terminology drift findings.
- Receives back from: updated feature artifacts, review findings, and repo docs as source evidence for later refresh.

Use this skill to keep humans, agents, docs, and implementation language aligned.

## Artifact Contract

Default repo artifact:

```text
docs/UBIQUITOUS_LANGUAGE.md
```

Default repo `AGENTS.md` pointer:

```markdown
- Shared language: read `docs/UBIQUITOUS_LANGUAGE.md` when planning, implementing, or reviewing domain terminology.
```

The language doc is generated and refreshed by the skill. It is not a locked
human-authored glossary.

## Workflow

1. Run `scripts/ubiquitous-language.py locate [--repo PATH]`.
2. Read the repo's `AGENTS.md`, `README.md`, and documentation contract when
   present.
3. Run `scripts/ubiquitous-language.py inventory [--repo PATH]` to collect
   candidate source files.
4. If the language doc or `AGENTS.md` pointer is missing, run init as a dry run
   first:

   ```bash
   scripts/ubiquitous-language.py init [--repo PATH]
   ```

5. Only write after the user approves repo mutation:

   ```bash
   scripts/ubiquitous-language.py init [--repo PATH] --write
   ```

6. Curate `docs/UBIQUITOUS_LANGUAGE.md` from authoritative repo evidence.
7. Run `scripts/ubiquitous-language.py lint [--repo PATH]`.

## Rules

- Default to `docs/UBIQUITOUS_LANGUAGE.md` for every repo.
- Do not create root `UBIQUITOUS_LANGUAGE.md`.
- Do not patch repo-local files from `setup.sh`; repo injection happens only
  when this skill is called.
- Focus on domain terms. Include harness workflow terms only when the active
  repo's domain is agent harness work.
- Compress aliases into preferred terms.
- One authoritative source is enough when evidence is clear.
- If a requested repo path is missing, fail clearly and suggest nearby paths;
  do not silently alias stale repo names.
- Keep output compact enough for agents to load before planning or review.

## Language Doc Schema

```markdown
# Ubiquitous Language

## Purpose

## Terms
| Term | Definition | Use When | Compress / Aliases | Avoid | Evidence |
|------|------------|----------|--------------------|-------|----------|

## Open Language Questions
| Question | Why It Matters | Evidence Needed |
|----------|----------------|-----------------|

## Refresh Notes
```
