# Skills

`skills/` is the source of truth for shared Claude and Codex skills.

![Current skills setup and workflows](../docs/diagrams/skills-current-state-workflows.png)

## Authoring Contract

Every retained skill must have:

- `SKILL.md`
- `skill.toml`
- a strict `## Composes With` section in `SKILL.md`

Minimum shape:

```text
skills/<name>/
├── SKILL.md
└── skill.toml
```

Expanded shape:

```text
skills/<name>/
├── SKILL.md
├── claude/SKILL.md      # optional thin runtime wrapper
├── codex/SKILL.md       # optional thin runtime wrapper
├── scripts/             # deterministic helpers
├── references/          # schemas, patterns, setup notes
├── assets/              # templates and static output assets
├── shared/              # runtime-neutral support
└── skill.toml
```

`## Composes With` schema:

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

Fill unused rows with `none`. Keep entries concrete: name the owning skill,
state file, helper script, artifact path, or runtime surface.

## Runtime Setup

`setup.sh` reads `skill.toml`.

Portable shared skill:

```toml
name = "wiki"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
```

Shared skill with runtime wrappers:

```toml
name = "spec-new-feature"
targets = ["claude", "codex"]
default_entry = "SKILL.md"
claude_entry = "claude/SKILL.md"
codex_entry = "codex/SKILL.md"
```

Codex-only skill:

```toml
name = "morning-sync"
targets = ["codex"]
default_entry = "SKILL.md"
```

Runtime install behavior:

| Runtime | Behavior | Implication |
|---------|----------|-------------|
| Claude | Symlinks selected entrypoint and shared dirs | Repo edits are visible immediately |
| Codex | Copies selected payload and shared dirs | Rerun `setup.sh` after skill edits |

Shared dirs installed with a skill:

- `scripts/`
- `assets/`
- `references/`
- `shared/`

## Composability Model

Skills should compose instead of duplicating ownership.

| Pattern | Meaning | Example |
|---------|---------|---------|
| Parent | Skill owns the current user request | `morning-sync` owns day-start summary |
| Child | Skill may be invoked as a narrower surface | `focus` mutates roadmap rows |
| Uses format | Borrow presentation without handing off ownership | `compare` uses `explain` visual modes |
| Reads state | Observe another surface without writing it | `morning-sync` reads roadmap rows |
| Writes through | Mutate only through the owning helper | `daily-review` drains completed rows through `focus` |
| Hands off | Transfer ownership to a better surface | `idea` hands code-grounded work to `spec-new-feature` |
| Receives back | Accept delivery reality from another workflow | `daily-review` receives completed-row state from `focus` |

Default ownership:

- `roadmap.md`: `focus`
- `state/ideas/<slug>/`: `idea`
- `docs/artifacts/<feature>/`: `spec-new-feature`
- `state/collab/daily-reviews/`: `daily-review`
- forensic session reports: `execution-review`

## Human Presentation

Human-presenting skills should be visual-first when they explain workflow,
architecture, planning, review, decisions, or proposed state.

Default ladder:

1. Link an existing Excalidraw diagram or create a new one for the shape of the
   work.
2. Give a short prose summary that names the decision or proposed state.
3. Use text, tables, file references, acceptance criteria, or code review for
   drill-down.

This applies most often to `morning-sync`, `focus`, `daily-review`,
`execution-review`, `spec-new-feature`, `idea`, `compare`, `explain`, and
`create-agents-md`.

Do not force a new diagram for one-line status updates, direct command output,
small mechanical edits, narrow line-specific review findings, or transient
progress messages. Reuse an existing diagram when it already explains the
current shape.

Keep this rule in human-facing docs and the relevant `SKILL.md` files. Do not
put Excalidraw-specific policy in `skills/AGENTS.md`.

## Human Response Contract

The response packet should stay short and readable: `Result`, `Visual`, `Gate`,
`Ledger`, one or more concrete `Next Actions`, and `Details` links.

`Visual` is always a slot. For workflow, architecture, planning, review,
decision, or multi-artifact work, link an existing diagram or create/render one.
For narrow mechanical work, say why no visual was useful.

Use `Ledger` when the session has multiple user requests, corrections, or
follow-ups. Track `Captured`, `Done`, `Not Done`, and `Parked` so nothing
disappears into chat.

Durable summary artifacts are conditional: create them only when the skill owns
a persistent record or the work benefits from one. Before final response, map
the latest user requests to the packet. Every request should be done, parked, or
called out as not done.

Examples:

- `spec-new-feature`: response packet plus linked spec or artifact set under
  `docs/artifacts/<feature>/`.
- `execution-review`: response packet plus a forensic report when the review
  needs a retained record.
- `daily-review`: response packet plus the drained daily review record in
  `state/collab/daily-reviews/`.
- Small or no-artifact work: response packet only.

## Research And Subagents

Research-heavy skills keep one parent skill as orchestrator. Use subagents only
when the user explicitly authorizes delegation or parallel work.

- Explorer: read-only factual investigation.
- Worker / Implementor: bounded file-scoped edits.
- Gate / Verifier: independent validation of changed files and commands.

For decontaminated research, Explorer sees approved questions or source paths,
not the desired answer. The parent skill reconciles conflicts and writes the
artifact through the owning surface.

## Dependency-Bearing Skills

If a skill has executable support:

1. Keep the model-facing workflow in `SKILL.md`.
2. Put helper code in `scripts/`.
3. Put setup notes, schemas, and external references in `references/`.
4. Put templates/static output assets in `assets/`.
5. Keep caches, virtual environments, browser installs, and generated state out
   of tracked source.
6. Run `~/.dot-agent/setup.sh` and verify both runtime installs.

## Excalidraw Diagram Skill

`excalidraw-diagram` is the diagramming surface for durable visual artifacts.

Use it when a workflow, architecture, or research artifact should have an
editable Excalidraw source and a rendered PNG.

Artifact contract:

```text
docs/diagrams/<slug>.excalidraw   # editable source of truth
docs/diagrams/<slug>.png          # rendered image for docs/review
```

Render with:

```bash
~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh \
  docs/diagrams/<slug>.excalidraw \
  docs/diagrams/<slug>.png
```

The renderer is cached under `~/.dot-agent/state/tools/`, not vendored into
tracked skill source. The skill workflow is:

```text
describe concept -> create .excalidraw -> render PNG -> inspect -> fix -> rerender
```
