---
status: draft
feature: harness-reduction
---

# Tasks: harness-reduction

## Execution Order

This is one end-to-end implementation wave, but tasks still have dependency
order so the wave can be verified and stopped cleanly.

1. Foundation contracts and principled locations.
2. Skill manifest schema and validator.
3. Context audit surface.
4. Root/runtime/doc reduction.
5. Representative skill migrations.
6. Setup/audit/doc verification.
7. North Star review against spec/design.

Execution requires explicit human go-ahead after this task artifact is approved.

## Task List

### HR-01: Lock Foundation References

Files:

- `skills/references/output-packet.md`
- `skills/references/subagent-delegation.md`
- `skills/references/roadmap-and-handoff-surfaces.md`
- `skills/references/skill-manifest-schema.md`
- `skills/AGENTS.md`
- `skills/README.md`
- `skills/references/skill-authoring-contract.md`

Work:

- Create shared references for repeated contracts.
- Document `skill.toml` schema v1.
- Keep official `SKILL.md` frontmatter portable.
- State that `skill.toml` carries local harness schema.
- Keep `## Composes With` as human/runtime-readable during transition.

Acceptance:

- Each reference has a clear owning purpose.
- `skills/AGENTS.md` points to references instead of restating details.
- `skills/README.md` remains human-facing and does not become giant policy
  prose.

Verify:

- `rg -n "output-packet|subagent-delegation|roadmap-and-handoff|skill-manifest-schema" skills`

Estimate:

- 2-3 hours.

Parallel safety:

- Can run in parallel with HR-02 only if file ownership is disjoint.

### HR-02: Add Skill Manifest Validator

Files:

- `scripts/validate-skill-manifests.py`
- `scripts/skill-instruction-audit.py`
- optionally `README.md`

Work:

- Add read-only validator using `tomllib`.
- Validate existing root keys without changing setup parsing assumptions.
- Validate optional v1 schema sections when present.
- Cross-check:
  - `skill.toml.name` equals folder name
  - `SKILL.md` frontmatter name equals folder name
  - `targets` contains known runtimes
  - selected entries exist
  - composed skills exist
  - declared scripts/references/assets exist
  - `## Composes With` exists while transition remains active
- Keep validator separate from setup until stable.
- Optionally have `skill-instruction-audit.py` call or mention it, but do not
  make setup depend on it yet unless implementation proves low risk.

Acceptance:

- Running validator on current repo produces structured findings without
  modifying files.
- Existing skills pass baseline checks, or findings are actionable and captured
  in HR-05 migration.

Verify:

- `python3 scripts/validate-skill-manifests.py`
- `python3 scripts/validate-skill-manifests.py --format json`

Estimate:

- 3-4 hours.

Parallel safety:

- Can run in parallel with HR-03.

### HR-03: Add Context Surface Audit

Files:

- Preferred: `skills/context-surface-audit/SKILL.md`
- Preferred: `skills/context-surface-audit/skill.toml`
- Preferred: `skills/context-surface-audit/scripts/context-surface-audit.py`
- Alternative if design changes during execution:
  `skills/execution-review/scripts/context-surface-audit.py`

Work:

- Add deterministic, privacy-preserving context audit.
- Report:
  - root/default instruction word counts
  - skill word counts
  - duplicate anchors such as `Human Response Contract`
  - runtime symlink/copy surfaces
  - manifest schema coverage
  - optional session metadata aggregates without transcript text
- Decide during implementation whether this is a standalone skill or belongs
  under `execution-review`; stop if ownership becomes unclear.

Acceptance:

- Audit reads source/runtime metadata without dumping private chat content.
- Output gives clear reduction targets and warnings.
- Skill composes with `execution-review` if standalone.

Verify:

- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --help`
- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --format text`
- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --format json`

Estimate:

- 3-5 hours.

Parallel safety:

- Can run in parallel with HR-02.

### HR-04: Reduce Root And Runtime Docs

Files:

- `AGENTS.md`
- `claude/CLAUDE.md`
- `README.md`
- `docs/harness-runtime-reference.md`
- `skills/improve-agents-md/assets/AGENTS.template.md`
- `skills/improve-agents-md/assets/CLAUDE.template.md`

Work:

- Trim duplicated response contract while preserving packet shape.
- Keep `AGENTS.md` in 350-650 word soft range, aiming near 400-500.
- Keep Claude usable but Codex-first.
- Fix README wording: Codex rules are synced/copied, not symlinked.
- Move setup/skill packaging detail behind principled references.
- Update templates so future generated instruction files preserve the reset.

Acceptance:

- Root remains concise and operationally complete.
- Claude entrypoint is aligned but not over-optimized.
- README/runtime docs do not contradict setup behavior.

Verify:

- `wc -w AGENTS.md claude/CLAUDE.md README.md docs/harness-runtime-reference.md`
- `rg -n "symlink.*rules|rules.*symlink" README.md docs/harness-runtime-reference.md setup.sh`
- `./setup.sh --check-instructions`

Estimate:

- 3-4 hours.

Parallel safety:

- Should run after HR-01 so references exist.

### HR-05: Migrate Representative Skill Manifests

Files:

- `skills/morning-sync/skill.toml`
- `skills/focus/skill.toml`
- `skills/spec-new-feature/skill.toml`
- `skills/execution-review/skill.toml`
- selected `SKILL.md` files only if references need narrow links
- all current `skills/*/skill.toml` files once the validator pattern is stable

Work:

- Add `schema_version = 1` and v1 TOML sections to representative skills.
- Keep existing root manifest keys unchanged.
- Because Ash requested max coverage, migrate every current source skill once
  validator + pattern are stable.
- Add narrow Markdown links to shared references where they replace repeated
  prose.

Acceptance:

- Representative manifests show source-of-truth pattern.
- Markdown `## Composes With` remains readable and consistent.
- Validator passes or explains remaining unmigrated skills.

Verify:

- `python3 scripts/validate-skill-manifests.py`
- `./setup.sh --check-instructions`

Max-coverage execution note:

- Include `idea` in the first pass.
- Include the new `context-surface-audit` skill.
- Prefer all-manifest migration if the validator stays clean.

Estimate:

- 2-4 hours.

Parallel safety:

- Can run after HR-02 and HR-01.

### HR-06: Wire Diagrams Into Design/Docs

Files:

- `docs/diagrams/harness-reduction-source-runtime.excalidraw`
- `docs/diagrams/harness-reduction-source-runtime.png`
- `docs/diagrams/harness-reduction-skill-schema.excalidraw`
- `docs/diagrams/harness-reduction-skill-schema.png`
- `docs/diagrams/harness-reduction-iteration-loop.excalidraw`
- `docs/diagrams/harness-reduction-iteration-loop.png`
- `docs/artifacts/harness-reduction/04_design.md`
- optionally `README.md` or `skills/README.md`

Work:

- Keep the three rendered diagrams as design artifacts.
- Link rendered PNGs from `04_design.md`.
- Add to README/skills README only if it improves human lookup without adding
  default-context bloat.

Acceptance:

- Diagrams are rendered PNGs from Excalidraw sources.
- No overlapping/clipped text in rendered images.

Verify:

- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/harness-reduction-source-runtime.excalidraw docs/diagrams/harness-reduction-source-runtime.png`
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/harness-reduction-skill-schema.excalidraw docs/diagrams/harness-reduction-skill-schema.png`
- `~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh docs/diagrams/harness-reduction-iteration-loop.excalidraw docs/diagrams/harness-reduction-iteration-loop.png`

Estimate:

- Already drafted; 0.5-1 hour for final wiring.

Parallel safety:

- Independent after design.

### HR-07: North Star Verification

Files:

- `docs/artifacts/harness-reduction/01_spec.md`
- `docs/artifacts/harness-reduction/03_research.md`
- `docs/artifacts/harness-reduction/04_design.md`
- `docs/artifacts/harness-reduction/05_tasks.md`

Work:

- Add final checklist or update this task file with verification results.
- Check implementation against:
  - Codex-first ergonomics
  - durable planning quality
  - portability preserved enough
  - principled locations
  - schema preserved/improved
  - non-schema prose reduced
  - deterministic checks added
  - setup/runtime source model preserved

Acceptance:

- Every design decision is implemented, deferred with reason, or explicitly
  marked out of scope.
- No unrelated dirty work is reverted.

Verify:

- `git diff --stat`
- `git diff -- AGENTS.md claude/CLAUDE.md README.md docs/harness-runtime-reference.md skills scripts docs/artifacts/harness-reduction`
- `./setup.sh --check-instructions`
- `python3 scripts/validate-skill-manifests.py`
- context audit command once created

Estimate:

- 1-2 hours.

Parallel safety:

- Final gate only; run after all edits.

## Boundaries

- Do not edit `/Users/ash/.codex` directly except by running setup.
- Do not change existing `skill.toml` root key formatting unless setup parsing
  is hardened first.
- Do not migrate every skill unless representative migration is stable.
- Do not preserve deleted experimental content inline; use git history or sparse
  archive ledger.
- Do not dump private transcript content in context audit output.
- Do not revert unrelated existing working-tree changes.

## Stop Conditions

- Validator design requires setup parser changes larger than expected.
- Context audit needs transcript content to be useful.
- Claude compatibility requires a separate design decision.
- Representative skill migration shows TOML/Markdown drift that cannot be
  linted cleanly.
- `setup.sh --check-instructions` fails in a way related to harness edits.

## Execution Results - 2026-04-23

Done:

- HR-01: Added shared references for output packets, delegation, roadmap/handoff
  ownership, and manifest schema.
- HR-02: Added `scripts/validate-skill-manifests.py` and a local TOML
  compatibility helper so audits work under Python 3.10+ without relying on
  user-site packages.
- HR-03: Added standalone `context-surface-audit` skill and deterministic
  structural audit script.
- HR-04: Reduced root, Claude, skill authoring, and skills README surfaces;
  fixed README wording for Codex rules sync/copy behavior.
- HR-05: Migrated every current source skill manifest to schema v1, including
  `idea` and `context-surface-audit`.
- HR-06: Kept existing rendered harness-reduction diagrams wired from design;
  no diagram source changes were needed.
- HR-07: Ran North Star verification against current main and adjusted stale
  instruction-template paths to `improve-agents-md`.

Verification:

- `python3 -m py_compile scripts/toml_compat.py scripts/validate-skill-manifests.py scripts/skill-instruction-audit.py scripts/repo-instruction-audit.py skills/context-surface-audit/scripts/context-surface-audit.py`: passed.
- `python3 scripts/validate-skill-manifests.py`: passed, 18/18 skills on schema v1.
- `python3 scripts/validate-skill-manifests.py --format json`: passed.
- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --format text`: passed.
- `python3 skills/context-surface-audit/scripts/context-surface-audit.py --format json`: passed and parsed as JSON.
- `node --check docs/artifacts/harness-reduction/generate-diagrams.mjs`: passed.
- Rendered all three harness-reduction Excalidraw diagrams with
  `skills/excalidraw-diagram/scripts/render-excalidraw.sh`: passed with no
  diagram diffs.
- Temp-home setup E2E install plus `./setup.sh --check-instructions`: passed
  without touching live `~/.codex` or `~/.claude`; skill audit checked 18
  skills and 32 runtime payloads.
- `rg -n "symlink.*rules|rules.*symlink" README.md docs/harness-runtime-reference.md setup.sh`: no stale README/runtime-reference wording.
- `git diff --check`: passed.

Open:

- `context-surface-audit` still identifies `skills/idea/SKILL.md` as the
  highest-context skill. That is now measured, not solved in this PR.
