---
status: approved
feature: ubiquitous-language-skill
---

# Feature Spec: ubiquitous-language-skill

## Goal

Create a reusable dot-agent skill that gives Codex/Claude and Ash a shared
repo vocabulary before planning, implementation, and review.

The skill should generate and refresh a concise repo-local ubiquitous language
artifact, then make that artifact discoverable through progressive disclosure
from the repo's `AGENTS.md`.

## Users and Workflows

- Ash calls the skill in any repo to create or refresh shared terminology.
- Feature planning uses the language artifact to keep specs, research, design,
  tasks, and implementation terms aligned.
- Reviews use the artifact to flag terminology drift in docs, instructions,
  architecture-heavy changes, and domain model changes.
- Repo-local examples such as semi-stocks use the same default location:
  `docs/UBIQUITOUS_LANGUAGE.md`.

## Acceptance Criteria

- A standalone `ubiquitous-language` skill can be installed into Codex and
  Claude runtime homes through dot-agent setup.
- The skill identifies the active repo root and chooses
  `docs/UBIQUITOUS_LANGUAGE.md` as the default artifact path.
- The skill can add one concise progressive-disclosure pointer to repo
  `AGENTS.md` when invoked in init/apply mode.
- The generated artifact is optimized for both humans and agents.
- The artifact focuses on repo domain terms; harness workflow terms only appear
  when the repo's domain is the harness itself.
- `spec-new-feature` automatically reads the language artifact before drafting
  `01_spec.md` when the artifact exists.
- `review` checks terminology drift when reviewing docs, instructions,
  architecture, domain model, or broad workflow changes.
- Setup does not automatically scan or mutate active repos for language drift.
- End-to-end implementation alignment is the primary success metric.

## Boundaries

- Do not make `setup.sh` patch project-local repositories. Setup installs the
  user-level skill only.
- Do not place language artifacts at repo root by default.
- Do not add a human-locking workflow in the first version; the artifact is
  agent-generated and refreshed by the skill.
- Do not build a heavy semantic extractor in the first version. Keep the first
  implementation deterministic where possible and model-curated where judgment
  is required.
- Do not silently alias stale repo paths. If `semi-stocks` is requested but
  missing, fail clearly and suggest the discovered `semi-stocks-2` path.

## Human Direction

- Use `docs/UBIQUITOUS_LANGUAGE.md` for all repos by default, including
  semi-stocks.
- Add a single progressive-disclosure line to `AGENTS.md` that points to the
  language doc.
- Optimize for both human reading and agent loading.
- The terms should depend on the repo and should primarily be domain terms.
- Keep evidence and refresh rules simple.
- Do not preserve human-authored locked definitions in the first version.
- Compress aliases into preferred terms.
- `spec-new-feature`: yes, read language docs automatically.
- `review`: yes, check terminology drift.
- `setup.sh`: no automatic language drift audit or repo mutation.
- Success metric: implementation alignment.

## Risks and Dependencies

- Repo-local doc contracts vary. The skill must inspect current repo docs and
  still default to `docs/UBIQUITOUS_LANGUAGE.md`.
- Updating only `AGENTS.md` may leave Claude-specific instruction surfaces less
  discoverable. First version keeps this intentional and can route future
  `CLAUDE.md` alignment through `improve-agents-md` if needed.
- A generated language doc can become stale. The skill needs `refresh` and
  `lint` paths before other skills rely on it heavily.
- Automatic extraction can overfit symbol names. The first version should
  inventory sources and let the agent curate definitions from evidence.
