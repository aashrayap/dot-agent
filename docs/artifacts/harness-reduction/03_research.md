---
status: draft
feature: harness-reduction
---

# Research: harness-reduction

## Flagged Items

- `/Users/ash/.dot-codex` is absent on this machine. Evidence:
  `ls /Users/ash/.dot-codex` failed. The active Codex runtime home is
  `/Users/ash/.codex`.
  Confidence: high.
- Local source is dirty and not identical to remote `origin/main`. Local branch:
  `codex/morning-focus-review-contract`; local HEAD: `82f97d9`; remote
  `refs/heads/main`: `5ae42cd`. Current working tree includes many unrelated
  modified/untracked files outside this artifact.
  Confidence: high.
- README says Codex rules are symlinked, but `setup.sh` copies/syncs
  `codex/rules/*` into `~/.codex/rules`. Evidence: `README.md` setup section
  vs `ensure_codex_rules`/`sync_dir_from_temp` in `setup.sh`.
  Confidence: high.
- Official-runtime docs are current as of 2026-04-23, but built-in system
  prompts themselves are not fully exposed as stable source. Treat doc behavior
  as evidence about load model, not as complete prompt de-duplication authority.
  Confidence: medium.

## Findings

### Codebase

1. `.dot-agent` is already the source of truth; runtime homes are consumers.
   Evidence:
   - `README.md` says `~/.dot-agent/` is versioned source and runtime homes are
     install targets.
   - `docs/harness-runtime-reference.md` repeats that `~/.claude/` and
     `~/.codex/` are install targets, not sources.
   - `setup.sh` sets `DOT_AGENT_HOME="$HOME/.dot-agent"`, `CLAUDE_DST`, and
     `CODEX_DST`, then links/copies into runtime homes.
   Confidence: high.

2. Direct Codex runtime edits are not needed for durable harness reduction.
   Source edits should land in `.dot-agent`; setup should propagate them.
   Runtime propagation differs by surface:
   - `~/.codex/AGENTS.md` symlink -> `/Users/ash/.dot-agent/AGENTS.md`
   - `~/.codex/config.toml` symlink -> `/Users/ash/.dot-agent/codex/config.toml`
   - `~/.codex/hooks.json` symlink -> `/Users/ash/.dot-agent/codex/hooks.json`
   - `~/.codex/rules/default.rules` regular copied file from
     `/Users/ash/.dot-agent/codex/rules/default.rules`
   - Codex skills are copied payloads, not symlinks.
   Confidence: high.

3. Verification already exists and should be the narrow gate for reduction.
   Evidence:
   - `./setup.sh --check-instructions` ran successfully.
   - Skill audit: 16 skills, 28 runtime payloads, no skill drift.
   - Repo audit: deterministic warnings remain for `/Users/ash/Documents` and
     `/Users/ash/Documents/2026/semi-stocks-2`, unrelated to this harness
     artifact.
   Confidence: high.

4. Default/root context is not enormous by itself, but duplication makes it
   expensive.
   Current counts:
   - `AGENTS.md`: 602 words
   - `claude/CLAUDE.md`: 458 words
   - `README.md`: 542 words
   - `docs/harness-runtime-reference.md`: 263 words
   - `skills/AGENTS.md`: 264 words
   - `skills/README.md`: 1,324 words
   - all source `skills/*/SKILL.md`: about 19,190 words total
   Confidence: high.

5. Root/default instruction duplication hotspots:
   - Human response contract appears in root, Claude entrypoint, skills README,
     and create-agents-md templates.
   - Operating loop appears in root and Claude entrypoint.
   - Source-of-truth/setup guidance appears in README, runtime reference, root
     AGENTS, skills AGENTS, and skills README.
   - Skill packaging rules appear in skills AGENTS, skills README, and runtime
     reference.
   Confidence: high.

6. Every source skill currently has `## Composes With`.
   Evidence: `for f in skills/*/SKILL.md; rg -q '^## Composes With'`.
   Missing output means no top-level source skill lacks the section.
   Confidence: high.

7. The current 7-row composability schema is already canonicalized in docs:
   `Parent`, `Children`, `Uses format from`, `Reads state from`, `Writes
   through`, `Hands off to`, `Receives back from`.
   Evidence: `skills/README.md`, `skills/AGENTS.md`, and
   `skills/references/skill-authoring-contract.md`.
   Confidence: high.

8. The highest-bloat source skills are not missing structure; they carry too
   much workflow/detail inline:
   - `idea`: 2,963 words
   - `execution-review`: 1,698 words
   - `spec-new-feature`: 1,408 words
   - `explain`: 1,401 words
   - `focus`: 1,361 words
   - `wiki`: 1,304 words
   Confidence: high.

9. Repeated semantic blocks across skills:
   - roadmap ownership/control plane rules
   - Excalidraw/durable visual escalation
   - handoff destinations
   - response packet structure
   - negative ownership boundaries
   - subagent/decontaminated research guidance
   Confidence: high.

10. Installed bundled Codex runtime skills are outside `.dot-agent` source
    control and do not follow the local composability schema:
    - `/Users/ash/.codex/skills/codex-primary-runtime/slides/SKILL.md`
    - `/Users/ash/.codex/skills/codex-primary-runtime/spreadsheets/SKILL.md`
    They are large vendor/system-like skills. Treat them as runtime inputs, not
    source targets for this pass unless a local wrapper policy is chosen.
    Confidence: high.

11. Session smoke test suggests root instructions are not the largest leak, but
    repeated contracts are real:
    - current root is about 4.1 KB / 602 words / 90 lines
    - recent session markers showed repeated root-contract and response-contract
      anchors in early rollout windows
    - triggered skills, pasted artifacts, runtime envelopes, and repeated
      AGENTS/project-doc blocks likely dominate first 0-200k token pollution
    Confidence: medium, because marker analysis avoids transcript content.

### Docs

1. The principled-location model already exists, but is split across too many
   places:
   - root `AGENTS.md`: always-on guidance and progressive-disclosure pointers
   - `README.md`: human architecture/setup overview
   - `docs/harness-runtime-reference.md`: setup/runtime packaging reference
   - `skills/AGENTS.md`: source-tree skill authoring contract
   - `skills/README.md`: human-facing skill catalog/composability model
   - `skills/references/skill-authoring-contract.md`: detailed schema and
     packaging rules
   Confidence: high.

2. The docs already support a clean split:
   - always-on repo instructions should stay small
   - setup and runtime install facts belong in runtime reference
   - skill authoring facts belong in `skills/AGENTS.md` plus references
   - human workflow catalog belongs in `skills/README.md`
   Confidence: high.

3. The bloat-prune-iterate loop is present as user direction in this artifact,
   not yet as an explicit harness doctrine in the source docs.
   Confidence: medium.

### External

1. OpenAI Codex docs support keeping `AGENTS.md` concise and layered.
   Official docs say Codex reads global and project `AGENTS.md` files before
   work, merges from broad to specific, and stops once the combined project-doc
   size reaches `project_doc_max_bytes`, 32 KiB by default:
   https://developers.openai.com/codex/guides/agents-md
   Confidence: high.

2. OpenAI Codex skill docs support progressive disclosure for skills.
   Codex starts with skill metadata, then loads full `SKILL.md` only when a
   skill is used. Skills may include `scripts/`, `references/`, and `assets/`.
   The docs also say keep each skill focused and prefer instructions over
   scripts unless deterministic behavior or external tooling is needed:
   https://developers.openai.com/codex/skills
   Confidence: high.

3. OpenAI Codex subagent docs support the requested orchestration direction.
   Codex can spawn specialized agents in parallel for codebase exploration and
   multi-step plans; it explicitly requires the user to ask for subagents; it
   also notes subagents consume more tokens than comparable single-agent runs:
   https://developers.openai.com/codex/subagents
   Confidence: high.

4. Claude Code docs support keeping `CLAUDE.md` concise and moving procedures
   into skills/rules.
   Claude docs say `CLAUDE.md` should hold facts needed every session, while
   multi-step procedures or path-specific content should move to skills or
   path-scoped rules. They also warn that files over 200 lines consume more
   context and can reduce adherence:
   https://code.claude.com/docs/en/memory
   Confidence: high.

5. Claude Code reads `CLAUDE.md`, not `AGENTS.md`; if a repo already uses
   `AGENTS.md`, Claude recommends a `CLAUDE.md` that imports it plus
   Claude-specific instructions. Current harness instead maintains a separate
   global Claude entrypoint with duplicated shared content.
   Confidence: high.

6. Public GitHub repo confirms the source/runtime model and Codex focus:
   repo tree includes `codex/`; README says `.dot-agent` is source of truth and
   installed runtime shape includes `~/.codex/AGENTS.md`, `config.toml`,
   `hooks.json`, `rules/`, and `skills/`:
   https://github.com/aashrayap/dot-agent
   Confidence: high.

### Cross-Ref

1. The most evidence-backed v1 reduction is not "delete half the root file".
   Root is already near a reasonable size. Better v1 target is de-duplicating
   repeated contracts and moving detailed shared policies behind principled
   references.
   Confidence: high.

2. `.dot-agent` should own canonical changes. `.codex` direct edits would fight
   setup because root/config/hooks are symlinks and skills/rules are generated
   consumers.
   Confidence: high.

3. "Every skill has composability" is already true for local source skills.
   The design problem is schema weight, field names, and how much repeated
   cross-skill policy lives in every `SKILL.md`.
   Confidence: high.

4. A 350-650 word range for root `AGENTS.md` is justified by:
   - current root at 602 words
   - smoke-test evidence that root is modest but repeated
   - Codex project-doc cap and layering model
   - Claude adherence warning for oversized instruction files
   Use 400-500 words as center, not a hard cap.
   Confidence: medium-high.

5. The deterministic/reasoning split can be made concrete with existing and
   proposed gates:
   - existing: `setup.sh --check-instructions`
   - existing: `skill-instruction-audit.py`
   - existing: `repo-instruction-audit.py`
   - existing execution-review scripts for session fetching/inspection
   - proposed: read-only context-surface audit for counts/anchors/loaded
     surfaces, avoiding transcript content
   Confidence: high for existing gates, medium for proposed gate.

## Patterns Found

- Source/runtime split is strong and should stay:
  `.dot-agent` source -> setup -> `.codex`/`.claude` consumers.
- Bloat tends to come from repeated policy prose, not missing abstractions.
- Skills are the right progressive-disclosure unit, but long skill bodies still
  leak when multiple skills compose.
- `Composes With` works as a cognitive map, but current 7 rows may be heavier
  than needed for leaf skills.
- The daily-loop skills repeat one contract: roadmap is the control plane,
  mutations go through `focus`, hidden project/session state is discouraged.
- The visual-reasoning skills repeat one contract: use `excalidraw-diagram` for
  durable human-facing workflow/architecture/before-after visuals.
- The safest delete/archive posture is: delete unused source, rely on git
  history, and optionally maintain a short archive ledger only for intentional
  removals that Ash may want to rediscover.
- Subagents reduce orchestrator context only when prompts are narrow and
  decontaminated; unbounded subagents can increase total tokens.

## Core Docs Summary

- `AGENTS.md`: should be the shortest always-on source of durable harness
  behavior for Codex/global repo use.
- `claude/CLAUDE.md`: should be a thin Claude-specific entrypoint. Current file
  duplicates root response/work-loop details.
- `README.md`: should remain human setup/architecture overview. It should not
  become agent default context.
- `docs/harness-runtime-reference.md`: should own setup, runtime install, and
  packaging facts.
- `skills/AGENTS.md`: should own source-tree skill authoring policy.
- `skills/README.md`: should own human-facing skill catalog, diagrams, and
  composability explanation.
- `skills/references/skill-authoring-contract.md`: should own detailed schema,
  source-only policy, packaging, ownership map, and subagent contracts.
- `setup.sh`: authoritative installer/audit gate. Current behavior matters more
  than prose in README when they conflict.

## Direction Options

### Option A: Minimal Root + Existing Schema

Keep current 7-row `Composes With` schema, trim only duplicated root/Claude
response contract, fix stale README setup wording, and add context-size checks.

Tradeoffs:
- Lowest risk.
- Preserves current skill docs.
- Leaves some schema bloat and repeated cross-skill contracts.

### Option B: Foundation Pattern Reset

Define a compact foundation contract, then apply it to only the central docs and
one or two representative skills before broad skill edits:

- root `AGENTS.md`: 400-500 word center target, 350-650 allowed range
- `claude/CLAUDE.md`: thin Claude-specific wrapper or import-like equivalent
- `skills/references/skill-authoring-contract.md`: canonical structure
- compact `Composes With` v2 fields:
  - `Trigger/Parent`
  - `Delegates To`
  - `Reads`
  - `Writes`
  - `Handoff/Returns`
  - optional `Format Source`
- shared reference docs for:
  - roadmap control plane
  - visual escalation
  - response packet
  - handoff surfaces
- deterministic `context-surface-audit.py` for counts, anchors, loaded
  surfaces, and drift signals

Tradeoffs:
- Matches Ash's "foundational pattern first" direction.
- Gives future parallel skill edits a clear target.
- Needs careful design before touching many skills.

### Option C: Aggressive Skill Diet

Immediately split large skills into thin `SKILL.md` entrypoints plus references,
starting with `idea`, `spec-new-feature`, `execution-review`, `focus`, and
`explain`.

Tradeoffs:
- Highest token reduction potential.
- Highest regression risk.
- Easy to break behavior unless composability foundation and deterministic
  checks land first.

### Recommended Default

Option B.

Reason: research shows the root is not the only leak, every local skill already
has composition, and `.dot-agent` already has the right source/runtime shape.
The next leverage point is a principled foundation that makes later parallel
skill compression deterministic instead of subjective.

## Open Questions

Direction answers captured 2026-04-23:

- Choose Option B, Foundation Pattern Reset, but do not over-optimize by
  shrinking the skill schema at the cost of structure. The schema itself is
  foundational; reduce the rest of skill prose around it.
- Root instruction target stays a soft range: 350-650 words, with 400-500 as
  center.
- Claude surface is lower priority for now: keep Claude usable, but optimize
  Codex-first and do not spend this pass heavily tuning Claude.
- Research whether a more structured output/schema way exists for defining
  skills in the harness before deciding the final schema design.
- Principled-location map is accepted.
- First-pass shared references should prioritize output packet, subagent /
  deterministic delegation, and a combined roadmap-control + handoff-surfaces
  reference. Visual escalation can wait unless diagram work needs it.
- Archive policy: use a single archive ledger only for meaningful removals;
  otherwise rely on git history.
- Context audit should start as a separate surface, probably its own skill or
  possibly part of `execution-review`; do not wire it directly into
  `setup.sh --check-instructions` yet.
- Implementation can be one end-to-end wave after careful design, with
  verification against the spec/North Star to keep moving.
- Produce more than one diagram if helpful, maximum three.

1. Should `claude/CLAUDE.md` become mostly a Claude-specific wrapper around the
   shared root contract, or stay a separate concise global Claude entrypoint?
2. Should `Composes With` v2 replace the 7-row schema now, or should design keep
   7 rows but define stricter brevity rules?
3. Should the archive ledger be a single `docs/archive.md`, a folder such as
   `docs/archive/`, or only commit messages plus git history?
4. Should bundled system skills like `codex-primary-runtime/slides` and
   `spreadsheets` stay out of scope entirely, or should local wrapper policy
   document why they are exempt?
5. Should context-surface audit become part of `setup.sh --check-instructions`
   immediately, or start as a separate script until stable?
