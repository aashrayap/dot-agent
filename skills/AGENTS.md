# Skills Instructions

This directory is the source of truth for shared Claude and Codex skills.

Use this file as the always-on skill authoring contract. Pull the detailed
schema and setup rules only when the current edit needs them.

## Skill Work Loop

- Keep `SKILL.md` lean: trigger, composition, core workflow, and direct links to
  deeper files.
- Move setup notes, schemas, examples, and provider/runtime variants into
  `references/`, `scripts/`, `assets/`, or `shared/`.
- Preserve runtime portability unless a skill's `skill.toml` targets only one
  runtime.
- Use existing skill owners before adding a new top-level skill.
- Verify source entries and installed payloads with setup/audit commands when
  skill edits should propagate.

## Composition Layers

- Every retained skill needs a strict `## Composes With` section near the top of
  `SKILL.md` when creating or materially rewriting it.
- Think in three layers:
  - Routing: `Parent`, `Children`, `Hands off to`, `Receives back from`
  - Borrowed shape: `Uses format from`
  - State/control: `Reads state from`, `Writes through`
- Keep composition rows concrete: skill names, helper scripts, canonical state
  files, artifact directories, or runtime surfaces.
- `Children` may be narrower owner skills or inline checkpoint helpers such as
  `grill-me` inside `spec-new-feature`.
- Keep legacy compatibility paths out of composition metadata unless the legacy
  path is still a normal-path surface. Put migration notes in the workflow body
  instead.
- Fill unused rows with `none`.
- Mutate another skill's state only through that skill's helper scripts or
  documented write path.

## Runtime Packaging

- Each skill should install through `~/.dot-agent/setup.sh`.
- Use `skill.toml` to declare targets, selected entrypoints, and machine-checkable
  schema v1 fields when present.
- Keep shared workflow logic at the skill root; use thin `claude/` or `codex/`
  wrappers only when runtime-specific syntax is necessary.
- Claude receives symlinks. Codex receives copied payloads, so rerun setup after
  skill edits that should affect Codex.

## Read When Needed

- Detailed composition examples, manifest baseline, source-only policy, skill
  ownership map, and subagent role contracts:
  `skills/references/skill-authoring-contract.md`
- Local `skill.toml` schema v1:
  `skills/references/skill-manifest-schema.md`
- Human-facing catalog and workflow map: `skills/README.md`
- Runtime install mechanics: `../setup.sh`
