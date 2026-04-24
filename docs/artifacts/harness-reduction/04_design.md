---
status: draft
feature: harness-reduction
---

# Design: harness-reduction

## Chosen Direction

Use the Foundation Pattern Reset.

This is not a broad deletion pass first. It is a one-wave reset of the harness
foundation so future deletion and skill compression can be done deterministically
and in parallel:

- keep `.dot-agent` as source of truth
- keep `~/.codex` and `~/.claude` as runtime consumers
- optimize Codex-first ergonomics before Claude polish
- preserve durable planning quality
- define principled locations for each kind of harness truth
- preserve and improve skill schema as foundational structure
- reduce non-schema skill prose and duplicated contracts
- add deterministic verification against the North Star
- produce diagrams after design and before implementation

Design diagrams:

- [source/runtime ownership](../../diagrams/harness-reduction-source-runtime.png)
- [skill schema and progressive disclosure](../../diagrams/harness-reduction-skill-schema.png)
- [bloat-prune-iterate loop](../../diagrams/harness-reduction-iteration-loop.png)

## Relevant Principles

- **Codex-first source model:** durable changes belong in `.dot-agent`; runtime
  homes are install targets.
- **Progressive disclosure:** always-on instructions stay small; details move to
  skills, references, scripts, docs, and artifacts.
- **Schema over prose drift:** composition, ownership, dependencies, and
  read/write contracts should become machine-checkable where practical.
- **Reasoning vs deterministic split:** use scripts and subagents to gather or
  verify facts; reserve orchestrator reasoning for synthesis and judgment.
- **Bloat-prune-iterate:** remove or move non-core material after experiments;
  keep useful rediscovery breadcrumbs only for meaningful removals.
- **Portable enough:** preserve Claude usability, but do not spend this pass
  optimizing Claude-specific behavior ahead of Codex.

## Decisions

### 1. Source And Runtime Boundaries

Decision:

- `.dot-agent` remains the canonical source for root instructions, runtime
  config, skill source, docs, scripts, and state helpers.
- Direct edits under `/Users/ash/.codex` are debugging-only unless a runtime bug
  proves source propagation cannot work.
- Codex copied payloads (`~/.codex/skills`, `~/.codex/rules`) are refreshed by
  `setup.sh`.

Options considered:

- Edit runtime directly: rejected because setup owns install targets.
- Split source across `.dot-agent` and `.dot-codex`: rejected locally because
  `/Users/ash/.dot-codex` is absent and `.dot-agent` already owns the model.

Affected areas:

- `README.md`
- `docs/harness-runtime-reference.md`
- `setup.sh`
- `codex/`
- `claude/`

Risk:

- README currently says Codex rules are symlinked, but setup copies/syncs them.
  Implementation must fix the stale wording or clarify "syncs".

### 2. Root Instruction Budget

Decision:

- Root `AGENTS.md` target is a soft 350-650 word range, with 400-500 as the
  normal center.
- No hard gate in the first wave.
- Root should carry only identity, response packet, operating loop, source
  boundaries, review rule, and progressive-disclosure pointers.

Options considered:

- Strict word cap: rejected for now; useful later after audits stabilize.
- No target: rejected because bloat needs a measurable pressure.

Affected areas:

- `AGENTS.md`
- `claude/CLAUDE.md`
- `skills/improve-agents-md/assets/AGENTS.template.md`
- `skills/improve-agents-md/assets/CLAUDE.template.md`

Risk:

- Over-compression can remove judgment. The root rewrite must preserve the
  North Star even if it does not hit the center range on first edit.

### 3. Claude Surface

Decision:

- Keep Claude usable but do not optimize it heavily in this pass.
- Keep `claude/CLAUDE.md` concise and aligned with source boundaries, but avoid
  a deep Claude-specific redesign.

Options considered:

- Thin wrapper around root: attractive but may need Claude-specific import
  behavior and more testing.
- Separate concise entrypoint: acceptable for now if duplicate prose is reduced.

Affected areas:

- `claude/CLAUDE.md`
- `claude/settings.json`
- improve-agents-md templates

Risk:

- Claude and Codex shared-contract drift remains possible until a deterministic
  template/audit checks shared fragments.

### 4. Skill Definition Structure

Decision:

- Preserve skill schema as a foundational part of the harness.
- Do not shrink schema just to save tokens.
- Move beyond Markdown-only composition by extending local `skill.toml` with a
  versioned, machine-checkable harness schema.
- Keep official `SKILL.md` frontmatter minimal and portable.
- Keep `## Composes With` in Markdown for human/runtime readability during the
  transition; lint or generate it from `skill.toml` later.

Official facts behind the decision:

- OpenAI Codex skills are still `SKILL.md` first: `name`, `description`, optional
  `scripts/`, `references/`, `assets/`, and optional `agents/openai.yaml`.
- Agent Skills frontmatter supports only general fields plus arbitrary
  `metadata`; it does not define typed composition.
- `agents/openai.yaml` supports Codex UI, invocation policy, and tool
  dependencies, not ownership/handoff/state graph.
- Local `skill.toml` already exists and setup ignores unknown keys if current
  root keys remain unchanged.

Proposed local schema v1:

```toml
name = "morning-sync"
targets = ["codex"]
default_entry = "SKILL.md"
schema_version = 1

[composition]
parents = []
children = ["focus", "daily-review", "idea", "spec-new-feature"]
formats = []
reads = ["state/collab/roadmap.md"]
writes = []
delegates = ["focus"]
handoffs = ["idea", "spec-new-feature", "daily-review"]

[contract]
inputs = ["daily planning request", "roadmap status request"]
outputs = ["chat packet: This Session Focus, Result, Next Actions"]
scripts = ["scripts/morning-sync-setup.sh"]
references = []
state_reads = ["state/collab/roadmap.md"]
state_writes = []
tools = []

[invoke]
implicit = true
explicit = ["morning-sync"]
```

Keep in Markdown:

- trigger nuance and non-goals
- workflow steps
- judgment boundaries
- examples and edge cases
- response style

Put in TOML:

- identity, runtime targets, entrypoints
- composition graph
- read/write ownership
- script/reference/asset dependencies
- declared inputs and outputs
- invocation flags
- schema version

Affected areas:

- `skills/*/skill.toml`
- `skills/*/SKILL.md`
- `skills/README.md`
- `skills/AGENTS.md`
- `skills/references/skill-authoring-contract.md`
- `scripts/skill-instruction-audit.py`
- new validator script

Risk:

- `setup.sh` parses TOML with shell text matching. The first wave must not
  alter existing one-line `targets`, `default_entry`, `claude_entry`, or
  `codex_entry` formats unless setup parsing is hardened first.

### 5. Shared References

Decision:

First-pass shared references:

- `skills/references/output-packet.md`
- `skills/references/subagent-delegation.md`
- `skills/references/roadmap-and-handoff-surfaces.md`
- `skills/references/skill-manifest-schema.md`

Deferred unless needed by diagram/design work:

- `skills/references/visual-escalation.md`

Rationale:

- Output packet, subagent delegation, roadmap control, and handoff surfaces are
  repeated across high-traffic skills.
- Visual escalation is useful but less central to the first reduction wave.

Risk:

- Moving text into references only helps if the skill bodies link them narrowly
  and do not restate them wholesale.

### 6. Context Surface Audit

Decision:

- Add a separate context-audit skill or script first; do not wire it into
  `setup.sh --check-instructions` immediately.
- It may compose with `execution-review`, but should start as a distinct
  deterministic surface if that keeps ownership clearer.

Likely v1:

- `skills/context-surface-audit/`
- `scripts/context-surface-audit.py`
- read-only output: word counts, duplicate anchors, loaded runtime symlinks,
  skill sizes, manifest schema coverage, and privacy-preserving session
  metadata aggregates.

Risk:

- If the audit becomes too forensic, it should move under `execution-review`.
  If it stays as structural context measurement, it can remain separate.

### 7. Archive Policy

Decision:

- Use git history for ordinary deletions.
- Add a single archive ledger only for meaningful removals:
  `docs/archive.md`.

Ledger entry shape:

```markdown
## <date> - <removed surface>

- Removed: `<path>`
- Reason:
- Last useful commit/ref:
- Replacement:
```

Risk:

- An archive doc can become another bloat surface. It should stay sparse and
  reference commits rather than preserving removed content.

### 8. One E2E Implementation Wave

Decision:

- After design approval, implementation can be a single end-to-end wave rather
  than separate batches.
- Use file-scoped tasks, subagents where authorized, and deterministic
  verification against this spec and design.

Wave should include:

- root/Claude/default instruction trim
- README/runtime-reference cleanup
- skill manifest schema doc
- shared references
- validator/audit scaffold
- representative manifest additions
- context audit skill or script
- before/after diagrams
- verification gates

Risk:

- One wave is efficient but can touch many files. Task file must define exact
  write scopes and stop conditions before execution.

### 9. Diagrams

Decision:

Produce up to three diagrams after design:

1. source/runtime ownership and install flow
2. skill schema and progressive-disclosure flow
3. bloat-prune-iterate loop with deterministic gates

Affected areas:

- `docs/diagrams/harness-reduction-source-runtime.*`
- `docs/diagrams/harness-reduction-skill-schema.*`
- `docs/diagrams/harness-reduction-iteration-loop.*`

Risk:

- Diagrams must not become a new maintenance burden. They should show stable
  ownership and flow, not every skill.

## Open Risks

- Current working tree contains unrelated modified and untracked files. The
  implementation wave must avoid reverting user work.
- Skill schema migration can create two sources of truth if TOML and Markdown
  drift. Validator should catch this before broad migration.
- `setup.sh` shell parsing limits how much TOML shape can change safely in one
  wave.
- Context audit must avoid dumping private transcript content.
- Claude drift may remain until a later pass if Codex-first scope holds.
- Official Codex skill metadata may evolve; local schema should stay namespaced
  and portable rather than pretending to be official runtime behavior.

## File Map

Primary source surfaces:

- `AGENTS.md`
- `claude/CLAUDE.md`
- `README.md`
- `docs/harness-runtime-reference.md`

Skill foundation:

- `skills/AGENTS.md`
- `skills/README.md`
- `skills/references/skill-authoring-contract.md`
- `skills/references/skill-manifest-schema.md`
- `skills/references/output-packet.md`
- `skills/references/subagent-delegation.md`
- `skills/references/roadmap-and-handoff-surfaces.md`

Representative skills for schema adoption:

- `skills/morning-sync/skill.toml`
- `skills/focus/skill.toml`
- `skills/spec-new-feature/skill.toml`
- `skills/execution-review/skill.toml`
- `skills/idea/skill.toml`

Max-coverage execution update:

- After validating the schema pattern, migrate every current source skill
  manifest rather than only the representative first set.
- Use current main's `improve-agents-md` path for instruction-template files.

Validation:

- `scripts/skill-instruction-audit.py`
- `scripts/validate-skill-manifests.py`
- possible `skills/context-surface-audit/`

Diagrams:

- `docs/diagrams/harness-reduction-source-runtime.excalidraw`
- `docs/diagrams/harness-reduction-source-runtime.png`
- `docs/diagrams/harness-reduction-skill-schema.excalidraw`
- `docs/diagrams/harness-reduction-skill-schema.png`
- `docs/diagrams/harness-reduction-iteration-loop.excalidraw`
- `docs/diagrams/harness-reduction-iteration-loop.png`

Verification gates:

- `./setup.sh --check-instructions`
- `python3 scripts/validate-skill-manifests.py`
- context audit command once created
- spec/North Star checklist in `05_tasks.md`
