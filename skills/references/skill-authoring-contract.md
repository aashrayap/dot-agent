# Skill Authoring Contract

Read this when creating or materially rewriting a skill, changing skill runtime
entrypoints, auditing skill installation, or delegating skill implementation.

## Composes With Schema

Every retained skill must declare how it composes with the harness. Add this
section near the top of each `SKILL.md`:

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

## Source-Only Policy

`skills/AGENTS.md` is author-time policy for the source tree. It is not
installed as runtime context for individual skills. Any rule needed while a
skill is being used must live in that skill's selected entrypoint, or in an
installed `scripts/`, `references/`, `assets/`, or `shared/` file that the
entrypoint explicitly tells the runtime to read.

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
