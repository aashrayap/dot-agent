# Skills

`skills/` is source for shared Claude and Codex skills.

![Current skills setup and workflows](../docs/diagrams/skills-current-state-workflows.png)

## At A Glance

Every retained skill needs:

- `SKILL.md`
- `skill.toml`
- a strict `## Composes With` section near the top

Use:

- [skills/AGENTS.md](/Users/ash/.dot-agent/skills/AGENTS.md) for the always-on
  authoring contract
- [skills/references/skill-authoring-contract.md](/Users/ash/.dot-agent/skills/references/skill-authoring-contract.md)
  for detailed examples and source-only policy
- [skills/references/skill-manifest-schema.md](/Users/ash/.dot-agent/skills/references/skill-manifest-schema.md)
  for local `skill.toml` schema v1 and validation
- [README.md](/Users/ash/.dot-agent/README.md) plus `setup.sh` for runtime
  install behavior

## Skill Shape

Optional directories:

```text
scripts/     deterministic helpers
references/  schemas, setup notes, lookup docs
assets/      templates and static output assets
shared/      runtime-neutral support
claude/      thin Claude wrapper when needed
codex/       thin Codex wrapper when needed
```

`SKILL.md` stays runtime-readable. It owns trigger nuance, core workflow,
judgment boundaries, and `## Composes With`.

`skill.toml` owns local machine-checkable structure: targets, entrypoints,
schema version, composition graph, contracts, declared paths, and invocation
flags.

## Composition Layers

Each `## Composes With` block has three jobs:

| Layer | Rows | What it answers |
| --- | --- | --- |
| Routing | `Parent`, `Children`, `Hands off to`, `Receives back from` | Who owns this request now, what narrower surface can be called, and where control moves next |
| Borrowed shape | `Uses format from` | Which skill's presentation or shape is reused without transferring ownership |
| State/control | `Reads state from`, `Writes through` | Which canonical surfaces are observed and which owner path mutates state |

Rules:

- Name canonical surfaces in metadata. Keep legacy paths in workflow notes.
- `Children` can be owner skills or checkpoint helpers.
- Use `Receives back from` only when returned state or outputs matter.
- Fill unused rows with `none`.

## Example: `spec-new-feature` Composing `grill-me`

This is the forward pattern for a checkpoint helper:

```markdown
## Composes With

- Parent: `idea`, `focus`, or `init-epic`
- Children: `ubiquitous-language` when repo terminology needs refresh; `grill-me` for pressure-test checkpoints; `excalidraw-diagram` when a durable visual helps
- Uses format from: `excalidraw-diagram` when a design visual materially helps
- Reads state from: `docs/UBIQUITOUS_LANGUAGE.md` when present, idea notes, roadmap rows, repo docs/code, and feature artifacts
- Writes through: `docs/artifacts/<feature>/`
- Hands off to: `focus`, `review`, or `daily-review`
- Receives back from: `focus`, `review`, PR refs, and prior feature artifacts
```

`grill-me` does not own the feature artifact set. It pressure-tests the current
phase, then `spec-new-feature` records the resolved notes in its own artifacts.

Use it at two checkpoints:

- after research, before design, when viable directions still have weak branches
- after design, before tasks or execution, when tradeoffs or failure modes still
  feel soft

## Runtime Setup

`setup.sh` reads `skill.toml`.

```toml
name = "wiki"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
schema_version = 1
```

Runtime-specific wrappers stay thin:

```toml
name = "spec-new-feature"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
claude_entry = "claude/SKILL.md"
codex_entry = "codex/SKILL.md"
schema_version = 1
```

Install behavior:

| Runtime | Behavior | Implication |
| --- | --- | --- |
| Claude | Symlinks selected entrypoint and shared dirs | Source edits are visible immediately |
| Codex | Copies selected skill payloads | Rerun `setup.sh` after skill edits |

## Default Owners

Default ownership lives in
[roadmap-and-handoff-surfaces.md](references/roadmap-and-handoff-surfaces.md).

| Surface | Owner |
| --- | --- |
| `state/collab/roadmap.md` | `focus` |
| `state/ideas/<slug>/` | `idea` |
| `docs/artifacts/<feature>/` | `spec-new-feature` |
| `docs/UBIQUITOUS_LANGUAGE.md` | `ubiquitous-language` |
| `state/collab/daily-reviews/` | `daily-review` |
| forensic session reports | `execution-review` |
| `AGENTS.md` / `CLAUDE.md` creation or improvement | `improve-agents-md` |
| external remote-review packets | `handoff-research-pro` |

## Workflow Groups

| Group | Entry Skill | Composes |
| --- | --- | --- |
| Daily loop | `morning-sync` | `focus`, `daily-review`, `idea`, `spec-new-feature` |
| Idea to PR | `idea` or `spec-new-feature` | `grill-me`, `init-epic`, `handoff-research-pro`, `review`, `focus` |
| Shared language | `ubiquitous-language` | `spec-new-feature`, `review`, `improve-agents-md` |
| Visual reasoning | `visual-reasoning` | `explain`, `compare`, `excalidraw-diagram` |
| Context/review | `context-surface-audit` or `execution-review` | structural counts vs forensic evidence |

Use the smallest owner surface that matches the user's ask, then compose child
skills instead of duplicating their workflows.

## State And Diagram Policy

- `roadmap.md` is the normal-path daily control plane.
- Legacy `focus.md` and `state/projects/*` are compatibility or history
  surfaces, not targets for new workflow design.
- Diagrams are optional receipts, not a default tax. Use
  `excalidraw-diagram` when workflow, architecture, or state shape would be
  harder to follow in prose alone.

## Shared References

- [skill-authoring-contract.md](references/skill-authoring-contract.md):
  source-only policy, minimum shape, setup contract.
- [skill-manifest-schema.md](references/skill-manifest-schema.md): local
  schema v1 and validation rules.
- [output-packet.md](references/output-packet.md): Ash-facing final packet.
- [subagent-delegation.md](references/subagent-delegation.md): role contracts
  when delegation is explicitly authorized.
- [roadmap-and-handoff-surfaces.md](references/roadmap-and-handoff-surfaces.md):
  state ownership and handoff paths.

## Verification

```bash
python3 scripts/validate-skill-manifests.py
python3 scripts/validate-skill-manifests.py --format json
python3 skills/context-surface-audit/scripts/context-surface-audit.py --format text
python3 skills/context-surface-audit/scripts/context-surface-audit.py --format json
./setup.sh --check-instructions
```

Use manifest validation for schema drift, context audit for context-surface
shape, and setup audit for installed runtime payload drift.
