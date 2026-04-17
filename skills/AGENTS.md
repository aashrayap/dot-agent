# Skills Instructions

This directory is the source of truth for shared Claude and Codex skills.

## Authoring Contract

Every retained skill must declare how it composes with the harness. Add a
`## Composes With` section near the top of each `SKILL.md` when creating or
materially rewriting a skill.

Required schema:

```markdown
## Composes With

- Parent:
- Children:
- Uses format from:
- Reads state from:
- Writes through:
- Hands off to:
- Receives back from:
```

Fill unused rows with `none`. Keep entries concrete: skill names, helper
scripts, state files, artifact directories, or runtime surfaces.

## Setup Contract

Each skill should install through `~/.dot-agent/setup.sh`; do not manually copy
tracked skill files into runtime homes except when debugging setup.

Required minimum:

```text
skills/<name>/
├── SKILL.md
└── skill.toml
```

Manifest baseline:

```toml
name = "<name>"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
```

Use `claude_entry` or `codex_entry` only for thin runtime wrappers. Keep shared
workflow logic at the skill root.

Shared directories installed with the selected entrypoint:

- `scripts/` for deterministic helpers
- `references/` for schemas, setup notes, and lookup docs
- `assets/` for templates and static output assets
- `shared/` for runtime-neutral support files

Claude receives symlinks. Codex receives copied payloads, so rerun setup after
skill edits.

## Composition Rules

- Prefer composing an existing owner over adding a new top-level skill.
- `focus` owns the daily roadmap.
- `projects` owns durable workstream state.
- `idea` owns incubation artifacts.
- `spec-new-feature` owns deep code-grounded feature artifacts.
- `execution-review` owns forensic retrospective review and session-quality recommendations.
- Mutate another skill's state only through that skill's helper scripts or
  documented write path.

## Subagent Roles

Use portable role contracts. Codex should spawn subagents only when the user has
explicitly authorized delegation or parallel work.

- Explorer: read-only factual investigation with evidence.
- Worker / Implementor: bounded edits in an assigned file/module scope.
- Gate / Verifier: independent validation, tests, and pass/fail findings.

The parent skill remains responsible for decomposition, context curation, and
final synthesis. Delegated tasks need role, goal, scope, inputs, output schema,
stop conditions, and verification expectations.

For decontaminated research, Explorer sees approved questions or source paths,
not the desired answer. The parent skill reconciles findings and writes the
artifact through the owning surface.
