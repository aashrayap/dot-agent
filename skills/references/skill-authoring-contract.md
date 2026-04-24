# Skill Authoring Contract

Read this when creating or materially rewriting a skill, changing skill runtime
entrypoints, auditing skill installation, or delegating skill implementation.

## Composition Layers

Every retained skill must declare how it composes with the harness. Keep this
section near the top of each `SKILL.md` so the runtime can read it:

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

Read the rows in three layers:

- Routing layer: `Parent`, `Children`, `Hands off to`, `Receives back from`
- Borrowed-shape layer: `Uses format from`
- State/control layer: `Reads state from`, `Writes through`

Fill unused rows with `none`. Keep entries concrete: skill names, helper
scripts, canonical state files, artifact directories, or runtime surfaces.

Pattern notes:

- `Children` can be a narrower owner skill or a checkpoint helper. Example:
  `spec-new-feature` can compose `grill-me` as a pressure-test child without
  changing feature-artifact ownership.
- `Writes through` should name the canonical owner path only. Keep migration or
  compatibility paths in the workflow body, not in composition metadata.
- `Receives back from` is optional bookkeeping for child or downstream outputs
  that meaningfully return structured state. Do not invent it for every child.

Example:

```markdown
## Composes With

- Parent: `idea`, `focus`, or `init-epic` when work needs code-grounded planning.
- Children: `grill-me` for pressure-test checkpoints; `excalidraw-diagram` when a feature plan needs a durable visual.
- Uses format from: `excalidraw-diagram` for human-facing planning visuals when useful.
- Reads state from: idea `spec.md`/`plan.md`, roadmap rows, repo docs/code, and feature artifacts.
- Writes through: `docs/artifacts/<feature>/` for feature artifacts.
- Hands off to: `focus`, `review`, or `daily-review`.
- Receives back from: `focus`, `review`, PR refs, and prior feature artifacts.
```

`skill.toml` carries the machine-checkable version of the same structure. See
`skills/references/skill-manifest-schema.md`.

## Source-Only Policy

`skills/AGENTS.md` is author-time policy for the source tree. It is not
installed as runtime context for individual skills. Any rule needed while a
skill is being used must live in that skill's selected entrypoint, or in an
installed `scripts/`, `references/`, `assets/`, or `shared/` file that the
entrypoint explicitly tells the runtime to read.

## Manifest Schema

`skill.toml` may also carry local schema v1 fields for validation and audit.
Runtime-visible behavior still belongs in `SKILL.md`. Keep the root install
keys stable and use schema v1 as the machine-checkable mirror of composition
and contract metadata. See `skills/references/skill-manifest-schema.md`.

## Minimum Shape

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
schema_version = 1
```

Use `claude_entry` or `codex_entry` only for thin runtime wrappers. Keep shared
workflow logic at the skill root.

Shared directories installed with the selected entrypoint:

- `scripts/` for deterministic helpers
- `references/` for schemas, setup notes, and lookup docs
- `assets/` for templates and static output assets
- `shared/` for runtime-neutral support files

## Setup Contract

Each skill should install through `~/.dot-agent/setup.sh`; do not manually copy
tracked skill files into runtime homes except when debugging setup.

Claude receives symlinks. Codex receives copied payloads, so rerun setup after
skill edits that should affect Codex.

## Ownership Map

- Prefer composing an existing owner over adding a new top-level skill.
- `focus` owns the daily roadmap.
- `idea` owns incubation artifacts.
- `spec-new-feature` owns deep code-grounded feature artifacts.
- `execution-review` owns forensic retrospective review and session-quality
  recommendations.
- Durable delivery state belongs in roadmap rows, feature artifacts, PRs, or
  explicit handoff docs. Do not recreate a hidden project/session service layer.
- Legacy surfaces such as `focus.md` or `state/projects/*` are compatibility or
  history, not new composition targets.

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
