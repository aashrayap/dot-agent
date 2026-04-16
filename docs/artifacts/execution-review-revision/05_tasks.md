---
status: draft
feature: execution-review-revision
---

# Tasks: Execution Review Revision

## Dependency Order

```text
T1 Skill packaging/docs rewrite
  ↓
T2 Shared schema + storage foundation
  ↓
T3 Codex adapter refactor
  ↓
T4 Claude adapter implementation
  ↓
T5 Unified setup/fetch/inspect CLIs
  ↓
T6 Review persistence + Hermes findings merge
  ↓
T7 Legacy cleanup + verification sweep
```

## Parallel-Safe Groupings

- `T1` is standalone and can be done first.
- `T2` must land before `T3`, `T4`, and `T6`.
- `T3` and `T4` can proceed in parallel after `T2`, but only if write sets stay disjoint.
- `T5` depends on `T3` and `T4`.
- `T6` depends on `T2` and `T5`.
- `T7` happens last.

## Tasks

### T1 — Rewrite skill packaging and runtime entrypoints

**Files**

- `skills/execution-review/skill.toml`
- `skills/execution-review/SKILL.md` (new)
- `skills/execution-review/codex/SKILL.md`
- `skills/execution-review/claude/SKILL.md` (new)

**Goal**

Turn execution-review into a dual-runtime skill with a shared core contract and thin runtime wrappers.

**Acceptance criteria**

- Skill targets both `claude` and `codex`.
- Shared core instructions describe the revised evidence-first system.
- Runtime wrappers are thin and do not duplicate the full logic.
- Old Codex-only workflow text is removed or clearly superseded.

**Verify**

```bash
sed -n '1,80p' skills/execution-review/skill.toml
sed -n '1,220p' skills/execution-review/SKILL.md
sed -n '1,220p' skills/execution-review/codex/SKILL.md
sed -n '1,220p' skills/execution-review/claude/SKILL.md
```

### T2 — Add shared schema and local storage foundation

**Files**

- `skills/execution-review/scripts/review_schema.py` (new)
- `skills/execution-review/scripts/review_store.py` (new)

**Goal**

Define the normalized session model, aggregate model, review history entry shape, optional identity config shape, and SQLite-backed local storage helpers under `~/.dot-agent/state/collab/execution-reviews/`.

**Acceptance criteria**

- Storage root resolves under `~/.dot-agent/state/collab/execution-reviews/`.
- SQLite schema exists for normalized session summaries and review metadata.
- History append helper exists for `history.jsonl`.
- Optional Hermes findings file contract is defined.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/review_schema.py \
  skills/execution-review/scripts/review_store.py
```

### T3 — Refactor Codex parsing into a runtime adapter

**Files**

- `skills/execution-review/scripts/codex_sessions.py`
- `skills/execution-review/scripts/codex_adapter.py` (new)

**Goal**

Keep the strong existing Codex parser but reshape it into an adapter that emits the new normalized schema and richer evidence bundles for response fit and skill leverage.

**Acceptance criteria**

- Existing Codex event reduction remains intact.
- Adapter emits normalized session summaries.
- Skill mentions, response-fit evidence inputs, and runtime policy fields are preserved.
- Existing aggregate behavior still works against the normalized model.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/codex_sessions.py \
  skills/execution-review/scripts/codex_adapter.py
python3 skills/execution-review/scripts/fetch-execution-sessions.py --runtime codex --window day >/tmp/execution-review-codex.json
python3 - <<'PY'
import json
data=json.load(open('/tmp/execution-review-codex.json'))
print(data['selection']['runtime'])
print(data['summary']['sessions'])
PY
```

### T4 — Implement Claude session adapter

**Files**

- `skills/execution-review/scripts/claude_adapter.py` (new)

**Goal**

Read Claude Code project-session artifacts and emit the same normalized session schema used by the Codex adapter.

**Acceptance criteria**

- Enumerates Claude sessions from `~/.claude/projects/`.
- Handles `sessions-index.json` when present and glob fallback when absent.
- Extracts session metadata, token usage, tool use, subagent count, verification-like signals, and response-fit evidence inputs.
- Gracefully tolerates undocumented schema drift.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/claude_adapter.py
python3 skills/execution-review/scripts/fetch-execution-sessions.py --runtime claude --window day >/tmp/execution-review-claude.json
python3 - <<'PY'
import json
data=json.load(open('/tmp/execution-review-claude.json'))
print(data['selection']['runtime'])
print(data['summary']['sessions'])
PY
```

### T5 — Replace the old setup/fetch/inspect scripts with unified CLIs

**Files**

- `skills/execution-review/scripts/execution-review-setup.py`
- `skills/execution-review/scripts/fetch-execution-sessions.py` (new)
- `skills/execution-review/scripts/inspect-execution-session.py` (new)
- `skills/execution-review/scripts/fetch-codex-sessions.py`
- `skills/execution-review/scripts/inspect-codex-session.py`

**Goal**

Expose one unified operational surface for setup, fetching, and deep inspection while preserving codex-only compatibility paths where practical.

**Acceptance criteria**

- Setup script reports the new script paths and storage location.
- Unified fetch script supports `--runtime codex|claude|all`.
- Unified inspect script can inspect a normalized session by runtime/session id.
- Old Codex-only fetch/inspect scripts either wrap the new path or are clearly marked legacy.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/execution-review-setup.py \
  skills/execution-review/scripts/fetch-execution-sessions.py \
  skills/execution-review/scripts/inspect-execution-session.py
python3 skills/execution-review/scripts/execution-review-setup.py day
python3 skills/execution-review/scripts/fetch-execution-sessions.py --runtime all --window day >/tmp/execution-review-all.json
```

### T6 — Add review persistence and Hermes findings merge

**Files**

- `skills/execution-review/scripts/review_store.py`
- `skills/execution-review/scripts/record-execution-review.py` (new)

**Goal**

Persist rendered reviews, append machine-readable history, and optionally merge matching Hermes findings into the final review entry.

**Acceptance criteria**

- Review markdown can be saved under `~/.dot-agent/state/collab/execution-reviews/reports/`.
- `history.jsonl` append works with the revised scorecard and metadata.
- Optional `hermes-findings.jsonl` entries can be matched and attached without breaking the core review path.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/record-execution-review.py
```

### T7 — Legacy cleanup and full verification sweep

**Files**

- touched files from T1–T6

**Goal**

Remove or clearly deprecate obsolete behavior, verify the new dual-runtime review pipeline end-to-end, and ensure the new artifact set is the active plan.

**Acceptance criteria**

- No skill docs still describe execution-review as Codex-only.
- New scripts compile cleanly.
- Basic fetch commands work for available runtimes.
- The new `docs/artifacts/execution-review-revision/` set is the active planning source.

**Verify**

```bash
python3 -m py_compile skills/execution-review/scripts/*.py
rg -n "Codex-only|only reads ~/.codex" skills/execution-review
git diff -- skills/execution-review docs/artifacts/execution-review-revision
```

## Out of Scope for This Execution Wave

- Full Hermes MCP bridge
- Automatic tracked-config mutation driven by Hermes
- Identity-split backfill or migration of old reviews
- Dashboard/UI work
