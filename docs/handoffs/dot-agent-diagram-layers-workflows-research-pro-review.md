# dot-agent Diagram Layers And Workflows: Research Pro Review Brief

## Reviewer Context

You are reviewing a local dot-agent documentation update that revises two
existing Excalidraw-backed diagrams:

- `docs/diagrams/dot-agent-runtime-architecture.png`
- `docs/diagrams/skills-current-state-workflows.png`

The diagrams are meant to give Ash a cleaner split between the agent harness
layers and the skill workflow model. After external diagram review, the
editable `docs/diagrams/*.excalidraw` files are the current source for these
two visuals; the older generators are now guarded so they do not overwrite
them. Treat this packet as the minimum source of truth. Repo paths below are
labels for the inline evidence blocks unless the access protocol says a remote
URL is current.

## Review Target And Mode

- Mode: architecture/design critique plus documentation review.
- Remote repo context: https://github.com/aashrayap/dot-agent
- Local target: uncommitted worktree on `main`.
- Base commit: `748bf2655e85ec313b32a089681bb6c9d150892d`.
- Requested scrutiny: challenge whether the two diagrams are factually aligned
  with the current repo state, separated cleanly enough, and free of stale
  workflow assumptions.

## Access Protocol

1. Confirm repo access: https://github.com/aashrayap/dot-agent
2. Use `Inline Evidence` as source of truth for the current local changes.
3. The pinned raw URLs below point to the base commit for remote repo context.
   They do not contain the uncommitted diagram revisions until this work is
   committed and pushed.
4. Treat branch, tree, blob, and raw `main` diagram links as context only until
   the updated diagrams are published.
5. If you cannot fetch any URL you rely on, cite the exact URL and stop instead
   of falling back to stale cached state.

## Source And Access Policy

- Primary evidence: this packet, the local editable Excalidraw sources, the
  local rendered PNGs, and the repo paths named below.
- Web/external sources: not needed. Use repository evidence only.
- Non-repo/local context: the worktree is dirty and the current diagram images
  are local until committed/pushed.
- Sensitive context check: no secrets, API keys, private user data, or
  irrelevant machine-local details are included.

## Primary Raw URLs

Pinned base context:

- https://raw.githubusercontent.com/aashrayap/dot-agent/748bf2655e85ec313b32a089681bb6c9d150892d/README.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/748bf2655e85ec313b32a089681bb6c9d150892d/skills/README.md
- https://raw.githubusercontent.com/aashrayap/dot-agent/748bf2655e85ec313b32a089681bb6c9d150892d/docs/artifacts/harness-reduction/generate-diagrams.mjs
- https://raw.githubusercontent.com/aashrayap/dot-agent/748bf2655e85ec313b32a089681bb6c9d150892d/docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs

Dynamic diagram links for context after publish:

- https://github.com/aashrayap/dot-agent/blob/main/docs/diagrams/dot-agent-runtime-architecture.png
- https://raw.githubusercontent.com/aashrayap/dot-agent/main/docs/diagrams/dot-agent-runtime-architecture.png
- https://github.com/aashrayap/dot-agent/blob/main/docs/diagrams/skills-current-state-workflows.png
- https://raw.githubusercontent.com/aashrayap/dot-agent/main/docs/diagrams/skills-current-state-workflows.png

## Goal

- Refresh existing diagram artifacts against the current repo state.
- Produce two separate visuals: one for agent harness layers, one for skill
  workflow and composition.
- Package the result for Research Pro review with repo and diagram links.

## General Direction

1. Keep `~/.dot-agent` as source of truth, with runtime homes as install
   targets.
2. Show Codex-first ergonomics without deleting Claude portability.
3. Show runtime skill metadata as first routing surface and `SKILL_INDEX.md` as
   fallback only.
4. Keep owner skills and durable write surfaces clear.

## Files To Review

Primary starting points, not hard boundaries:

- `README.md`
- `skills/README.md`
- `docs/artifacts/harness-reduction/generate-diagrams.mjs`
- `docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs`
- `docs/diagrams/dot-agent-runtime-architecture.excalidraw`
- `docs/diagrams/skills-current-state-workflows.excalidraw`
- `docs/diagrams/dot-agent-runtime-architecture.png`
- `docs/diagrams/skills-current-state-workflows.png`

## Inline Evidence

`README.md` lines 5-11 and 161-165

```text
The root README embeds docs/diagrams/dot-agent-runtime-architecture.png.
It says ~/.dot-agent is source of truth, runtime homes are install targets,
and machine-local state stays under gitignored state/.
It now says agents use runtime skill metadata first, and SKILL_INDEX.md is
the generated fallback index for ambiguous routing and state ownership.
```

Explanation: this is the root contract the harness diagram must reflect.

`skills/README.md` lines 5-11 and 125-141

```text
The skills README embeds docs/diagrams/skills-current-state-workflows.png.
It says agents should use runtime skill metadata first, then SKILL_INDEX.md
only for ambiguous routing or state ownership.
The Agent Routing Index section says SKILL_INDEX.md is a small fallback router
and does not replace runtime skill metadata or the target SKILL.md.
```

Explanation: this is the source wording behind the skill workflow diagram.

`skills/README.md` lines 54-61 and 143-154

```text
Composition rows answer routing, borrowed shape, and state/control questions.
Workflow groups include daily loop, idea to PR, shared language, visual
reasoning, and context/review.
```

Explanation: the second diagram should make these ownership lanes visible
without turning `SKILL_INDEX.md` back into the primary routing surface.

`docs/diagrams/dot-agent-runtime-architecture.excalidraw`

```text
Current editable source for "dot-agent Harness Layers".
It separates source layer, setup/routing/source rules, runtime homes, local
write surfaces, and audit gates.
It names runtime metadata first, SKILL_INDEX fallback only, Codex-first daily
path, portable Claude path, and failed checks flowing back to source fixes.
```

Explanation: this Excalidraw source is now the durable editable source for the
root harness PNG.

`docs/diagrams/skills-current-state-workflows.excalidraw`

```text
Current editable source for "dot-agent skill workflow layers".
The first lane is "Skill resolution layer":
user request -> runtime skill metadata -> read SKILL.md -> optional fallback
SKILL_INDEX.md -> owner skill selected -> receipt/state/artifact/handoff.
The remaining lanes show skill artifact contract, owner workflows, and runtime
target roster.
```

Explanation: this is the key distinction between skill routing and harness
installation.

`docs/artifacts/harness-reduction/generate-diagrams.mjs`

```text
This generator no longer writes dot-agent-runtime-architecture.excalidraw.
Its comment says the runtime architecture diagram is maintained directly under
docs/diagrams after external diagram review.
```

Explanation: this avoids generator drift after adopting the externally reviewed
manual Excalidraw source.

`docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs`

```text
This generator no longer writes skills-current-state-workflows.excalidraw.
It still writes the adjacent research-pro-review-gate artifact, but the main
skills workflow diagram is maintained directly under docs/diagrams.
```

Explanation: this keeps the main workflow overview distinct and prevents the
old generator path from overwriting reviewed diagram layout.

`docs/diagrams/dot-agent-runtime-architecture.png`

```text
Rendered local PNG. Visual inspection showed no text clipping after final
layout pass. Rendered dimensions: 8120 x 5392.
```

Explanation: this is the human-facing root README diagram.

`docs/diagrams/skills-current-state-workflows.png`

```text
Rendered local PNG. Visual inspection showed no text overlap after the final
artifact-contract row height fix. Rendered dimensions: 9128 x 7644.
```

Explanation: this is the human-facing skills README diagram.

## Review Breadth

Inspect adjacent docs, generator scripts, skill manifests, and existing diagram
policy when needed. Keep broader findings tied to whether the two diagrams help
Ash understand harness layers versus skill workflow.

## Non-Repo Context Included

- User asked for revised existing Excalidraw diagrams based on current repo
  state.
- User wanted two separate diagrams: agent harness layers and skill workflow.
- User also asked for a Research Pro handoff and links to existing diagrams
  with the dot-agent GitHub repo link.
- Current worktree has uncommitted changes, so GitHub branch links may be stale
  until commit/push.

## Assumptions And Blind Spots

Assumptions to falsify:

1. "Agent hardness" in the request meant "agent harness" - current evidence is
   the dot-agent repo domain and existing runtime architecture diagram - a user
   correction would disprove this.
2. Existing diagrams to revise are the two README-linked diagrams - current
   evidence is `README.md` and `skills/README.md` image embeds - a different
   intended diagram pair would disprove this.
3. `SKILL_INDEX.md` should be represented as fallback only - current evidence
   is the dirty README and skills README wording - contradictory skill metadata
   or setup behavior would disprove this.

Reviewer blind spots:

- You cannot rerun the local renderer unless you have the repo and runtime
  dependencies.
- The updated PNGs are local until pushed.
- Some dirty files predated this diagram pass.

## What Changed

`docs/diagrams/dot-agent-runtime-architecture.excalidraw`

- Adopted the supplied improved root runtime architecture visual as direct
  Excalidraw source.
- Added explicit source, setup, runtime, local state, and audit gate layers.
- Added runtime metadata first and `SKILL_INDEX.md` fallback-only language.

`docs/diagrams/skills-current-state-workflows.excalidraw`

- Adopted the supplied improved skills diagram as direct Excalidraw source.
- Split skill resolution, artifact contract, owner workflows, and runtime
  target roster.
- Kept daily loop, idea to PR, review/external gate, and knowledge/docs/visual
  workflows in separate lanes.
- Applied a local renderer layout fix so the artifact-contract text does not
  clip at the box edge.

Generator drift guards

- Updated both old generator scripts so they intentionally do not overwrite the
  two reviewed `docs/diagrams/*.excalidraw` sources unless the manual layouts
  are ported back into generator code later.

## Validation Already Run

- Earlier generator runs passed during the first drafting pass.
- After external review adoption, these two README diagrams are maintained as
  direct `.excalidraw` sources under `docs/diagrams/`.
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/dot-agent-runtime-architecture.excalidraw docs/diagrams/dot-agent-runtime-architecture.png`: passed.
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/skills-current-state-workflows.excalidraw docs/diagrams/skills-current-state-workflows.png`: passed.
- `python3 -m json.tool docs/diagrams/dot-agent-runtime-architecture.excalidraw >/dev/null`: passed.
- `python3 -m json.tool docs/diagrams/skills-current-state-workflows.excalidraw >/dev/null`: passed.
- Visual inspection of both rendered PNGs: passed after final layout fix.
- `git diff --check`: passed after final diagram and handoff edits.

## Known Out Of Scope

- Pre-existing dirty files not authored by this diagram pass include
  `AGENTS.md`, `README.md`, `codex/config.toml`,
  `docs/harness-runtime-reference.md`, `scripts/generate-skill-index.py`,
  `skills/AGENTS.md`, `skills/README.md`, and `skills/SKILL_INDEX.md`.
- Pre-existing untracked paths include `docs/artifacts/mattpocock-skill-compare/`,
  `docs/handoffs/spec-new-feature-grill-me-pr45-handoff-research-pro-review.md`,
  and `scripts/__pycache__/`.
- This packet does not review the broader skill-index simplification diff.

## Findings Intake Plan

Returned findings should be triaged into:

- fix now: diagram source edits, generator drift guards, and rerendered PNGs.
- backlog: a follow-up roadmap or docs task if the critique is broader than
  these two diagrams.
- local verification: renderer, JSON, setup, manifest, or index checks.
- reject with reason: record in chat or a follow-up handoff note.

## Review Tasks

Please review for:

1. Are the harness-layer and skill-workflow diagrams distinct enough, or do
   they duplicate concepts in a confusing way?
2. Do the diagrams match the repo's current "runtime metadata first,
   SKILL_INDEX fallback only" contract?
3. Do the workflow lanes represent state ownership accurately without reviving
   stale `projects/*` or hidden session-memory assumptions?
4. Are any diagram labels misleading, overloaded, or too implementation-heavy
   for human review?
5. Should this handoff wait for a commit/push before relying on GitHub diagram
   links?

## Bonus Scope

If time allows, briefly audit nearby docs for stale diagram captions or
contradictions with the new two-diagram split. Keep bonus findings separate
from primary review findings.

## Desired Reviewer Output

Lead with findings. For each finding include:

- severity: blocker, high, medium, low
- file/path
- issue
- why it matters
- suggested fix

If there are no blocking findings, say that explicitly and list polish
suggestions separately.
