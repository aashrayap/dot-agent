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

## Read When Needed

- Detailed authoring and source-only policy:
  `skills/references/skill-authoring-contract.md`
- Manifest schema:
  `skills/references/skill-manifest-schema.md`
- Output packet:
  `skills/references/output-packet.md`
- Delegation roles:
  `skills/references/subagent-delegation.md`
- Roadmap/handoff ownership:
  `skills/references/roadmap-and-handoff-surfaces.md`
- Human-facing catalog and diagrams:
  `skills/README.md`
