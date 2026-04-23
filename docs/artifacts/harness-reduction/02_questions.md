---
status: approved
feature: harness-reduction
---

# Research Questions: harness-reduction

## Human Direction

Answers captured 2026-04-23:

- Research and design the whole harness.
- Treat `.dot-agent` as source of truth and Codex runtime surfaces as
  consumers; inspect setup behavior before deciding whether direct runtime edits
  are needed.
- Preserve principled locations and consistent structure as foundational goals.
- Produce a flexible token-budget range from research instead of picking a hard
  limit upfront.
- Priority order: Codex-first ergonomics, durable planning quality,
  portability.
- Prefer delete or archive-note-with-commit-reference over parking experimental
  material in default context.
- Establish composability foundation for every skill, then execute broad skill
  updates later in parallel.
- Produce a before/after diagram after design and before implementation.
- Use subagents and deterministic checks to reduce orchestrator context
  pollution.

Approved for research.

1. What is the first reduction target: root repo instructions, skill files,
   `.dot-codex` runtime config, or the whole harness loop?
2. What token budget should define success for the universal repo instruction
   surface: 500, 1k, 2k, or "as short as possible after preserving judgment"?
3. Which principle is least negotiable during pruning: portability,
   Codex-first ergonomics, durable planning quality, or agent safety?
4. Should experimental material be deleted when unused, moved to archive, or
   parked under state/docs with clear "not default context" boundaries?
5. For composability schema, should every skill get a required block now, or
   should only workflow/orchestration skills get it first?
6. Should this reduction produce a durable before/after diagram, or is the chat
   + markdown artifact trail enough for this pass?
7. Should research inspect both repos equally, or should `.dot-agent` be treated
   as source of truth and `.dot-codex` as installed/runtime consumer unless
   evidence says otherwise?

## Codebase

1. Which files in `/Users/ash/.dot-agent` and `/Users/ash/.dot-codex` are loaded
   by default into agent context for common Codex and Claude Code sessions?
2. Which root instruction files duplicate the same operating guidance across
   repo, runtime, and installed surfaces?
3. Which scripts or manifests install, sync, audit, or package skills between
   source repos and runtime homes?
4. Which skill files currently contain composability-like structure, and which
   high-traffic skills lack it?
5. Which files currently encode Codex-specific assumptions, Claude-specific
   assumptions, or cross-runtime compatibility rules?
6. Which docs or state files are referenced from always-on instructions versus
   only through progressive disclosure?
7. Which setup or audit command proves that a reduced source harness still
   installs cleanly into runtime targets?

## Docs

1. What do the harness runtime reference, skills README, and skills AGENTS files
   define as canonical source, install target, and packaging policy?
2. Where do existing docs already describe the intended bloat-prune-iterate
   operating loop, if anywhere?
3. Which docs are still useful as deep references but should not be visible in
   default orchestrator context?
4. Which workflow diagrams or catalog docs would become stale if composability
   schema becomes required?

## Patterns

1. What is the smallest common instruction set repeated across successful recent
   repo instructions?
2. Which skill blocks consistently help agents choose the right next step, and
   which blocks mostly restate generic behavior?
3. Which workflows already use parent/child/handoff structure in practice?
4. Which recurring token leaks come from repeated response contracts, repeated
   safety rules, duplicated runtime setup facts, or excessive skill prose?
5. Which instructions can be replaced by local lookup rules, scripts, schemas,
   or artifact conventions?

## External

1. What current Codex and Claude Code built-in system/developer prompts or docs
   already cover behavior that the harness currently repeats?
2. What current runtime docs constrain how concise AGENTS.md / CLAUDE.md files
   should be structured?
3. Are there current best practices for modular skill or command composition
   that should influence the composability schema?

## Cross-Ref

1. Which repeated instructions are safe to delete because runtime built-ins,
   repo-level defaults, or skill-level rules already cover them?
2. Which high-value instructions must remain in default context because moving
   them behind a lookup would likely degrade behavior?
3. Which candidate deletions would break install/audit behavior across
   `.dot-agent` and `.dot-codex`?
4. Which composability fields are justified by actual workflow transitions
   versus speculative taxonomy?
5. What is the smallest coherent v1 reduction that can be verified without
   redesigning the full harness?
