# Skills

`skills/` is the source of truth for shared Claude and Codex skills.

## At A Glance

Every retained skill needs:

- `SKILL.md`
- `skill.toml`
- a strict `## Composes With` section near the top

Use:

- [skills/AGENTS.md](/Users/ash/.dot-agent/skills/AGENTS.md) for the always-on
  authoring contract
- [skills/references/skill-authoring-contract.md](/Users/ash/.dot-agent/skills/references/skill-authoring-contract.md)
  for detailed examples and manifest rules
- [skills/references/skill-manifest-schema.md](/Users/ash/.dot-agent/skills/references/skill-manifest-schema.md)
  for local `skill.toml` schema v1
- [README.md](/Users/ash/.dot-agent/README.md) plus `setup.sh` for runtime
  install behavior

## Composition Layers

The current composition layer in each skill is a 7-row contract with three
jobs:

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
- Children: `grill-me` for pressure-test checkpoints; `excalidraw-diagram` when a durable visual helps
- Uses format from: `excalidraw-diagram` when a design visual materially helps
- Reads state from: idea notes, roadmap rows, repo docs/code, and feature artifacts
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

## Default Owners

- `state/collab/roadmap.md`: `focus`
- `state/ideas/<slug>/`: `idea`
- `docs/artifacts/<feature>/`: `spec-new-feature`
- `docs/UBIQUITOUS_LANGUAGE.md`: `ubiquitous-language`
- `state/collab/daily-reviews/`: `daily-review`
- forensic session reports: `execution-review`
- `AGENTS.md`/`CLAUDE.md` improvement or creation: `improve-agents-md`
- external remote-review packets: `handoff-research-pro`

## Workflow Groups

| Group | Entry Skill | Composes |
| --- | --- | --- |
| Daily loop | `morning-sync` | `focus`, `daily-review`, `idea`, `spec-new-feature` |
| Idea to PR | `idea` or `spec-new-feature` | `grill-me`, `init-epic`, `handoff-research-pro`, `review`, `focus` |
| Shared language | `ubiquitous-language` | `spec-new-feature`, `review`, `improve-agents-md` |
| Visual reasoning | `visual-reasoning` | `explain`, `compare`, `excalidraw-diagram` |

## State And Diagram Policy

- `roadmap.md` is the normal-path daily control plane.
- Legacy `focus.md` and `state/projects/*` are compatibility or history
  surfaces, not targets for new workflow design.
- Diagrams are optional receipts, not a default tax. Use
  `excalidraw-diagram` when workflow, architecture, or state shape would be
  harder to follow in prose alone.

## Details Live Here

- authoring contract: [skills/AGENTS.md](/Users/ash/.dot-agent/skills/AGENTS.md)
- detailed schema and manifests:
  [skills/references/skill-authoring-contract.md](/Users/ash/.dot-agent/skills/references/skill-authoring-contract.md)
- manifest schema:
  [skills/references/skill-manifest-schema.md](/Users/ash/.dot-agent/skills/references/skill-manifest-schema.md)
- runtime install mechanics: [README.md](/Users/ash/.dot-agent/README.md)
- response contract: [AGENTS.md](/Users/ash/.dot-agent/AGENTS.md)
- durable diagram workflow:
  [skills/excalidraw-diagram/SKILL.md](/Users/ash/.dot-agent/skills/excalidraw-diagram/SKILL.md)
