---
status: complete
feature: skills-readme-current-state-diagram
---

# Research: skills-readme-current-state-diagram

## Flagged Items

- None. Local docs, setup script, manifests, and skill entrypoints agree on the
  current model.

## Findings

### Codebase

**Which README contains the diagram?**
Answer: `skills/README.md` embeds `../docs/diagrams/skill-workflow-prune-map.png`.
Confidence: high.
Evidence: `skills/README.md` first section.
Conflicts: none.
Open: none.

**What defines setup and install behavior?**
Answer: `setup.sh` is the install path. It enforces `~/.dot-agent` as canonical
home, symlinks Claude config and Claude skill entrypoints, symlinks Codex root
config/rules, copies Codex skill payloads, installs shared `scripts/`, `assets/`,
`references/`, and `shared/`, and backs up conflicting runtime files under
`state/backups/setup/`.
Confidence: high.
Evidence: `setup.sh`, `README.md`, `AGENTS.md`, `skills/README.md`.
Conflicts: none.
Open: none.

**Which current files define high-level workflows?**
Answer: `README.md` and skill entrypoints define four durable workflow groups:
daily loop (`morning-sync`, `focus`, `daily-review`), idea/planning/delivery
(`idea`, `init-epic`, `spec-new-feature`, `review`), forensic/comparison
(`execution-review`, `compare`, `review`), and docs/knowledge/visuals
(`wiki`, `create-agents-md`, `explain`, `compare`, `excalidraw-diagram`).
Confidence: high.
Evidence: `README.md` Human Daily Loop; `skills/*/SKILL.md` `Composes With`
sections and workflow sections.
Conflicts: none.
Open: none.

**What e2e checks exist?**
Answer: No package-level test runner exists in the repo. The meaningful e2e
checks for this doc/diagram change are rendering the Excalidraw PNG and running
`./setup.sh` to verify the current harness install still succeeds.
Confidence: high.
Evidence: repo file list, `setup.sh`, `skills/README.md` Dependency-Bearing
Skills section.
Conflicts: none.
Open: none.

### Docs

**Repo-level requirements.**
Answer: `AGENTS.md` says `claude/` and `codex/` are repo-side runtime config,
`skills/` is source of truth, `state/` is local, and runtime homes are install
targets. It also requires `skill.toml`, `## Composes With`, and setup-driven
runtime install.
Confidence: high.
Evidence: `AGENTS.md`.
Conflicts: none.
Open: none.

**Skill authoring requirements.**
Answer: `skills/AGENTS.md` requires `SKILL.md`, `skill.toml`, strict
`## Composes With`, root workflow logic, thin runtime wrappers, and shared dirs
for deterministic helpers, references, assets, and runtime-neutral support.
Confidence: high.
Evidence: `skills/AGENTS.md`.
Conflicts: none.
Open: none.

### Patterns

**Diagram style and README placement.**
Answer: README currently starts with a rendered PNG before the authoring
contract. The replacement should remain a rendered PNG, but the content should
be a current-state orientation map instead of a prune/target comparison.
Confidence: high.
Evidence: `skills/README.md`; existing rendered diagram.
Conflicts: none.
Open: none.

**Workflow grouping pattern.**
Answer: The current harness uses explicit ownership and handoffs instead of a
hidden project/session state layer. Human-facing state lives in roadmap rows,
feature artifacts, idea artifacts, PRs, handoff docs, wiki pages, diagrams, and
execution-review reports.
Confidence: high.
Evidence: `README.md`, `skills/README.md`, `skills/focus/SKILL.md`,
`skills/spec-new-feature/SKILL.md`, `skills/execution-review/SKILL.md`.
Conflicts: none.
Open: none.

### External

- None used.

### Cross-Ref

**Does current setup align across docs and code?**
Answer: Yes. `AGENTS.md`, `README.md`, `skills/README.md`, `skills/AGENTS.md`,
`setup.sh`, and `skill.toml` manifests all describe source-of-truth skill files
installed into Claude/Codex runtime homes by setup.
Confidence: high.
Evidence: all inspected files above.
Conflicts: none.
Open: none.

**Does stale current/target/published wording remain near README diagram?**
Answer: The stale wording is in the old diagram image and its artifact docs, not
in surrounding `skills/README.md` prose. The README image reference should move
to a new current-state diagram with updated alt text.
Confidence: high.
Evidence: `skills/README.md`; existing `skill-workflow-prune-map.png`.
Conflicts: none.
Open: none.

## Patterns Found

- README diagrams are tracked as `docs/diagrams/<slug>.excalidraw` plus rendered
  `docs/diagrams/<slug>.png`.
- Durable workflow docs use short labels, ownership lanes, and arrows for
  read/write or handoff paths.
- Skill docs separate authoring/runtime setup from human workflows; the diagram
  can summarize both without replacing the prose below it.

## Core Docs Summary

- `~/.dot-agent/` is canonical source.
- `setup.sh` is the runtime installer.
- `skills/` is source of truth.
- `skill.toml` decides runtime targets and entrypoints.
- `SKILL.md` plus `## Composes With` is the contract for skill behavior.
- Claude receives symlinked skill entrypoints/shared dirs; Codex receives copied
  payloads and needs `setup.sh` after edits.
- Current high-level workflows are daily loop, idea/planning/delivery,
  review/forensics, and docs/knowledge/visuals.

## Open Questions

- None blocking.
