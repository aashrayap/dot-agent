---
status: approved
feature: skills-readme-current-state-diagram
---

# Design: skills-readme-current-state-diagram

## Relevant Principles

- Human-facing docs should lead with a visual when explaining workflow or
  architecture.
- `skills/` is source of truth; runtime homes are install targets.
- Current workflow ownership should be explicit and human-readable.
- Avoid reviving old published/current-target workflow framing in the README.

## Decisions

### D1: Replace the README image with a new current-state workflow map

Decision: Create `docs/diagrams/skills-current-state-workflows.excalidraw` and
render `docs/diagrams/skills-current-state-workflows.png`, then point
`skills/README.md` at the PNG.

Options considered:
- Update old `skill-workflow-prune-map` in place.
- Add a new current-state diagram and leave old prune-map artifacts as historical
  artifacts.

Rationale: A new slug prevents stale prune/target semantics from living in the
README path while avoiding unrelated deletion of historical artifacts.

Affected areas: `skills/README.md`, `docs/diagrams/`.

Risks still open: none.

### D2: Make the diagram summarize setup plus workflows

Decision: Use three visual levels:
- source/install pipeline
- authoring contract
- high-level workflow lanes

Options considered:
- workflow-only diagram
- setup-only diagram
- combined current-state map

Rationale: The user asked for the diagram to reiterate/summarize the prose below
it and talk through high-level workflows. The README prose covers authoring,
runtime setup, composability, human presentation, response contract, subagents,
dependency-bearing skills, and Excalidraw. A combined map gives a human reader
the shape before the details.

Affected areas: diagram content only.

Risks still open: none.

### D3: Use a generated Excalidraw source for maintainability

Decision: Add a small generator under the feature artifact directory and use it
to emit the Excalidraw source.

Options considered:
- manually edit JSON
- reuse old prune generator
- add a focused generator for this diagram

Rationale: The existing diagram family already used a generator. A focused
generator keeps layout reproducible without changing the historical prune
generator.

Affected areas: `docs/artifacts/skills-readme-current-state-diagram/`.

Risks still open: none.

### D4: Move the Human Response Contract to the top of runtime-facing instructions

Decision: Place the Human Response Contract immediately below the root
`AGENTS.md` title and at the start of `claude/CLAUDE.md`.

Options considered:
- Leave the section in its existing lower position.
- Duplicate the contract.
- Move it to the top in both files.

Rationale: The user explicitly asked for the contract to be top-loaded in the
same PR. Moving avoids duplicate guidance and makes the response shape visible
before runtime setup details.

Affected areas: `AGENTS.md`, `claude/CLAUDE.md`.

Risks still open: none.

## Open Risks

- Rendered PNG readability must be checked visually after render.

## File Map

- `skills/README.md` — update diagram image reference and alt text.
- `docs/diagrams/skills-current-state-workflows.excalidraw` — editable diagram
  source.
- `docs/diagrams/skills-current-state-workflows.png` — rendered README image.
- `docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs` —
  reproducible diagram generator.
- `AGENTS.md` — move Human Response Contract to the top.
- `claude/CLAUDE.md` — move Human Response Contract to the top.
