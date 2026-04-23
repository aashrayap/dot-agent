---
status: approved
feature: hermes-always-on-thesis
---

# Research Questions: hermes-always-on-thesis

## Human Direction

1. What should "always on" mean for scope: all local agent sessions, only dot-agent harness sessions, only active roadmap project roots, or only explicitly opted-in workspaces?
2. Should the daily document be append-only, curated, or split into raw intake plus curated Hermes synthesis?
3. Should Hermes only report findings, or may it also draft proposed roadmap/focus mutations that wait for approval?
4. Is the candidate centralized thesis in `01_spec.md` directionally right, or should Hermes optimize for a different purpose?
5. What would make this feature not worth doing: too much noise, too much background activity, too much durable state, or unclear ownership?

### Resolved

1. Scope is `dot-agent` and `semi-stocks-2`, including work inside those roots.
2. Use two documents: appended intake log plus curated synthesis/thesis, with a further human presentation distillation available.
3. Suggestions are allowed, but first implementation should stay simple and low-permission.
4. Optimize for workflow clarity and non-forward-progress detection, especially identifying loops.
5. Keep the first slice simple; avoid noise and overbuilt durable state.

## Codebase

1. Where are Hermes findings currently generated, stored, read, and displayed?
2. Which scripts or skills already read `hermes-findings` state, and what schema do they expect?
3. What existing mechanisms can run background or recurring harness work without inventing a new daemon?
4. What current state helpers or conventions create per-day documents or daily review artifacts?
5. Which workflow surfaces currently own roadmap mutation, focus mutation, daily review closure, and execution review findings?
6. Where are raw execution identifiers, transcript anchors, and dependency graph internals filtered out of human-facing output?

## Docs

1. What do the harness runtime docs say about install targets, machine-local state, automation setup, and portable runtime behavior?
2. What do `execution-review`, `morning-sync`, `daily-review`, and `focus` skill docs say about ownership boundaries?
3. What docs define whether Hermes is a reviewer, memory surface, audit layer, or planning input?
4. What docs define where durable feature, review, and daily artifacts should live?

## Patterns

1. Which existing feature artifacts use a central operating thesis plus daily notes or append-only logs?
2. Which existing scripts separate raw evidence, synthesized findings, gates, and human-approved mutations?
3. Which existing background or setup paths are default-on, and how do they expose opt-out or pause behavior?
4. Which docs provide a concise daily human surface without duplicating the roadmap?

## External

1. What current Codex automation or heartbeat behavior is available for background work in this app/runtime?
2. Are there official runtime constraints that affect sub-hour background checks, local thread heartbeats, or recurring prompts?
3. Are there relevant privacy or persistence limits for storing AI-generated daily operational notes in local files?

## Cross-Ref

1. How should Hermes daily notes relate to `roadmap.md`, morning sync output, daily review output, and execution review findings without creating competing sources of truth?
2. What minimum schema lets Hermes write daily findings now while preserving a path to richer background automation later?
3. Which signal should be authoritative when the centralized thesis, roadmap focus, and recent execution evidence disagree?
4. What migration path turns Hermes on by default while keeping existing workflows usable during rollout?
