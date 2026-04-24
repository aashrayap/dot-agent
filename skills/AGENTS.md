# Skills Instructions

This directory is source for shared Claude and Codex skills. `setup.sh`
installs selected payloads into runtime homes; do not treat runtime copies as
source.

## Authoring Loop

- Keep `SKILL.md` lean: trigger, `## Composes With`, core workflow, and narrow
  links to deeper files.
- Put schemas, setup notes, examples, provider/runtime variants, and long
  patterns in `references/`, `scripts/`, `assets/`, or `shared/`.
- Preserve portability unless `skill.toml` targets only one runtime.
- Prefer composing an existing owner over adding a new top-level skill.
- Verify source entries and installed payloads after edits that should
  propagate.

## Required Shape

Every retained skill needs:

- `SKILL.md`
- `skill.toml`
- `## Composes With` near the top of `SKILL.md`

Runtime-readable composition stays in Markdown. Machine-checkable structure
lives in `skill.toml` using schema v1 from
`skills/references/skill-manifest-schema.md`.

## Composition Layers

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
- Use `skill.toml` to declare targets, selected entrypoints, and
  machine-checkable schema v1 fields.
- Keep shared workflow logic at the skill root; use thin `claude/` or `codex/`
  wrappers only when runtime-specific syntax is necessary.
- Claude receives symlinks. Codex receives copied payloads, so rerun setup after
  skill edits that should affect Codex.

## Read When Needed

- Detailed authoring and source-only policy:
  `skills/references/skill-authoring-contract.md`
- Manifest schema:
  `skills/references/skill-manifest-schema.md`
- Agent-readable routing and composition index:
  `skills/SKILL_INDEX.md`
- Output packet:
  `skills/references/output-packet.md`
- Delegation roles:
  `skills/references/subagent-delegation.md`
- Roadmap, handoff, and shared-language ownership:
  `skills/references/roadmap-and-handoff-surfaces.md`
- Human-facing catalog and diagrams:
  `skills/README.md`
- Runtime install mechanics:
  `../setup.sh`
