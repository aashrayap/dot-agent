# Skill Manifest Schema

`skill.toml` is the local harness schema for source-side validation. It does not
replace Codex or Claude runtime skill loading. Runtime-visible instructions
remain in `SKILL.md`, including `## Composes With`.

## Baseline

Keep these root keys stable because `setup.sh` reads them with simple shell
parsing:

```toml
name = "skill-name"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
claude_entry = "claude/SKILL.md" # optional
codex_entry = "codex/SKILL.md"   # optional
schema_version = 1
```

`targets` supports `claude` and `codex`.

## Schema Version 1

```toml
[composition]
parents = []
children = []
formats = []
reads = []
writes = []
delegates = []
handoffs = []

[contract]
inputs = []
outputs = []
scripts = []
references = []
assets = []
state_reads = []
state_writes = []
tools = []

[invoke]
implicit = false
explicit = []
```

## Field Meaning

- `composition.parents`: owning skills or broad parent contexts.
- `composition.children`: local skills or helpers this skill may invoke.
- `composition.formats`: skills whose output format may be borrowed.
- `composition.reads`: state, docs, files, or runtime evidence read by the
  skill.
- `composition.writes`: state, docs, files, or artifacts the skill writes.
- `composition.delegates`: local skill names or helper roles used for narrower
  work.
- `composition.handoffs`: local skills or external surfaces that can take over
  ownership.
- `contract.inputs`: common user intents or source inputs.
- `contract.outputs`: expected delivery surfaces.
- `contract.scripts`, `references`, `assets`: paths relative to the skill root.
- `contract.state_reads`, `state_writes`: durable state paths, usually under
  `state/` or `docs/`.
- `contract.tools`: required external tools or runtime connectors.
- `invoke.implicit`: whether matching user language may trigger the skill.
- `invoke.explicit`: explicit invocation names or command phrases.

## Validation

Run:

```bash
python3 scripts/validate-skill-manifests.py
python3 scripts/validate-skill-manifests.py --format json
```

The validator checks manifest shape, selected entrypoints, `SKILL.md`
frontmatter names, declared dependency paths, local composed skill names, and
presence of `## Composes With`.
