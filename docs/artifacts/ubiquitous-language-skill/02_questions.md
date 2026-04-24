---
status: approved
feature: ubiquitous-language-skill
---

# Research Questions: ubiquitous-language-skill

## Human Direction

- Artifact path: default to `docs/UBIQUITOUS_LANGUAGE.md`.
- Semi-stocks path: use docs, same as all repos.
- Artifact audience: both human reading and agent loading.
- Term scope: depends on repo; primarily domain terms.
- Evidence: keep it simple.
- Human-authored locks: no first-version lock model.
- Aliases: compress aliases to preferred terms.
- `spec-new-feature` integration: yes.
- `review` terminology drift: yes.
- Setup language audit: no.
- Stale repo aliasing: unresolved by user; design resolves by failing clearly
  with suggestions.
- Success metric: implementation alignment.

## Codebase

1. Where should the skill source live?
   - Answer: `skills/ubiquitous-language/`.
2. Does setup need custom skill wiring?
   - Answer: likely no; `setup.sh` already discovers skill directories with
     `skill.toml`. Verification should prove install.
3. Where should repo mutation happen?
   - Answer: inside the invoked skill/helper, not setup.

## Docs

1. Which dot-agent docs need progressive disclosure?
   - Answer: root `AGENTS.md` should get one line pointing to the dot-agent
     language doc once that doc exists.
2. Which repo-local docs get injected?
   - Answer: `AGENTS.md` gets one line; generated language doc goes under
     `docs/`.

## Patterns

1. Does this belong inside `spec-new-feature`?
   - Answer: no. `spec-new-feature` should consume it, not own it.
2. Does this belong inside `review`?
   - Answer: no. `review` should use it for drift checks, not own generation.
3. Does this belong inside `improve-agents-md`?
   - Answer: no. `improve-agents-md` may align instruction surfaces later.

## External

- No external research needed for first design. User supplied the DDD
  ubiquitous-language definition and target behavior.

## Cross-Ref

- The skill must compose with `spec-new-feature`, `review`,
  `improve-agents-md`, and repo-local skills without taking ownership of their
  state.
