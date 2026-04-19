# Repo Instruction Propagation Audit

Status: report-first audits implemented
Date: 2026-04-19

## Problem

Harness-level instruction changes do not automatically reach active project
repos. Runtime setup updates `~/.claude`, `~/.codex`, and installed skills, but
project-local `AGENTS.md` and `CLAUDE.md` remain independent. When repo-specific
chats load local instructions, harness contracts can drift silently.

Recent example: `.dot-agent/AGENTS.md` had the Human Response Contract, but
`semi-stocks-2/AGENTS.md` and `semi-stocks-2/CLAUDE.md` did not. Repo-specific
final responses therefore missed packet slots like `Visual` and `Ledger`.

## Current Setup Reality

- `setup.sh` enforces `~/.dot-agent` as canonical harness home.
- `setup.sh` symlinks Claude config into `~/.claude`.
- `setup.sh` symlinks Codex root `AGENTS.md` into `~/.codex/AGENTS.md`.
- `setup.sh` installs shared skills into Claude/Codex runtime homes.
- `setup.sh` runs report-only instruction audits after runtime install.
- `setup.sh` does not update project-local `AGENTS.md` or `CLAUDE.md`.

That behavior is correct for safety, but incomplete for propagation.

## Implemented Audit Surface

Implemented on 2026-04-19:

- `scripts/skill-instruction-audit.py`
- `scripts/repo-instruction-audit.py`
- report-only setup integration in `setup.sh`

Current setup output:

```text
Skill Instruction Audit
Checked 14 skills, 24 runtime payloads.
OK: no skill instruction drift found.

Repo Instruction Audit
Checked 3 repo roots from 26 discovered path(s).
OK: no repo instruction drift found.
```

Both audit scripts are read-only by default. `--strict` exists for CI or manual
gates, but setup does not use it.

The first setup audit reported missing `response-contract` and
`runtime-preference` fragments in `/Users/ash/Documents/2026/AGENTS.md` and
`/Users/ash/Documents/2026/CLAUDE.md`; those local instruction files were patched
in-session after the report.

## Original Active Repo Scan Findings

Read-only scan sources used:

- Codex trusted projects from `codex/config.toml` and `~/.codex/config.toml`
- recent execution-review normalized session CWDs
- git root normalization

Original observed active git roots before audit implementation and workspace
patches:

| Repo | AGENTS.md | CLAUDE.md | Contract status |
| --- | --- | --- | --- |
| `~/.dot-agent` | present | missing | harness source OK for Codex |
| `/Users/ash/Documents/2026` | present | present | fixed after setup audit reported drift |
| `/Users/ash/Documents/2026/semi-stocks-2` | present | present | fixed in current session |
| `/Users/ash/Documents/2026/tracker` | present | present | missing Human Response Contract |
| trader worktree | missing | present | missing Human Response Contract |
| conductor semi-stocks worktree | present | present | missing Human Response Contract |

Conclusion: repo-local instruction drift was present beyond `semi-stocks-2`.

## Design Recommendation

Add a report-first repo instruction audit, not an automatic merge.

```text
dot-agent update
    |
    v
setup.sh updates runtime homes
    |
    v
repo-instruction-audit.py scans active repos
    |
    v
findings table in setup output
    |
    v
human confirms patch/apply/ignore per repo
```

## Active Repo Discovery

Use multiple sources, then normalize to git roots:

1. Codex trusted projects in config.
2. Recent Codex/Claude session CWDs from execution-review state.
3. Roadmap active project names only when they map to known local paths.
4. Optional allowlist file, e.g.
   `state/collab/active-repos.toml`, for repos that should always be audited.

Do not scan every directory under `~/Documents` by default.

## Merge Safety Model

Never blindly rewrite repo instruction files.

Safe default:

- audit only
- output findings
- generate candidate patch files or unified diffs
- require user confirmation before editing

If automated edits are later added, use managed blocks:

```markdown
<!-- dot-agent:managed response-contract v1 sha256:<hash> -->
... portable contract text ...
<!-- /dot-agent:managed response-contract -->
```

Rules:

- Only replace content inside matching managed markers.
- If no managed block exists, propose insertion location but do not apply
  unless confirmed.
- Preserve repo-specific content outside markers.
- Keep `AGENTS.md` runtime-portable; do not insert Claude-only
  `<important if>` blocks.
- Keep `CLAUDE.md` aligned with facts, but allow Claude-specific blocks there.
- Detect user edits inside managed blocks with hash mismatch and report
  `manual review required`.
- Back up before writing, using existing setup backup conventions.

## Contract Fragment Model

Treat reusable harness content as named fragments, not full-file templates:

| Fragment | Target | Purpose |
| --- | --- | --- |
| `response-contract` | `AGENTS.md`, `CLAUDE.md` | human final packet shape |
| `runtime-preference` | `AGENTS.md`, `CLAUDE.md` | Codex preferred, runtime portable |
| `skill-composition` | repo root files | shared skill routing principles |

Fragment checks should use anchors plus optional block hashes. Full-file diffs
are too risky because repo instructions carry local authority.

## Skill Instruction Propagation

The same drift class exists for `skills/AGENTS.md`, but the fix is different.

Current reality:

- `skills/AGENTS.md` is source-tree authoring policy.
- `setup.sh` installs each selected skill entrypoint plus `scripts/`,
  `assets/`, `references/`, and `shared/`.
- `setup.sh` does not install `skills/AGENTS.md` into `~/.codex/skills` or
  `~/.claude/skills`.
- A runtime skill invoked from another repo should not rely on a relative
  `skills/AGENTS.md` path.

Immediate fix applied on 2026-04-19:

- Marked `skills/AGENTS.md` as author-time only.
- Removed runtime `skills/AGENTS.md` references from live skill entrypoints.
- Inlined the small portable subagent role mapping where skills need it.

Longer-term recommendation:

```text
skills/AGENTS.md
    |
    v
named skill-runtime contracts
    |
    v
setup.sh bundles selected contracts into each runtime skill payload
    |
    v
SKILL.md explicitly reads or embeds the contracts it depends on
```

Use runtime folders for reusable support, but do not treat them as authority.
The source of truth should stay in `.dot-agent`; runtime homes are generated
install targets. Critical behavior should be short and inline in `SKILL.md`.
Longer optional behavior can live under installed `shared/` or `references/`
files, with the entrypoint explicitly naming when to read it.

Possible schema extension:

```toml
runtime_contracts = ["subagent-roles@v1", "artifact-handoff@v1"]
```

Audit rules:

- Flag any installed skill whose entrypoint references `skills/AGENTS.md`.
- Flag manifests whose declared runtime contracts are missing from the installed
  payload.
- Flag contract changes that were not followed by `setup.sh`.
- Prefer generated managed blocks only for small, critical clauses.

## Execution Review Integration

Execution-review should add repo instruction drift as a first-class batch
signal.

Inputs:

- session CWDs in review window
- normalized git roots
- local `AGENTS.md` / `CLAUDE.md`
- required fragment anchors from harness source

Output sections:

- `Repo Instruction Drift`
- `Missing Required Fragments`
- `Response Fit Correlation`

Risk logic:

- If sessions in a repo have response-fit correction signals and that repo is
  missing response-contract anchors, raise severity.
- If a repo has no local instruction file, flag as missing local authority.
- If `AGENTS.md` and `CLAUDE.md` disagree on shared facts, flag split-brain
  instruction risk.
- If managed block hash changed locally, flag manual review required.

This makes batch review catch the cause, not just symptoms like follow-up
corrections.

## Suggested Implementation Slices

1. Add read-only `scripts/repo-instruction-audit.py`. Done.
2. Add fragment source files under `shared/instruction-fragments/`.
3. Teach `setup.sh` to run audit after normal install and print findings only.
   Done.
4. Add optional `--apply-confirmed` or separate patch command later.
5. Import the same audit module into `execution-review` rendering.
6. Add docs/tests around managed-block replacement and hash mismatch behavior.
7. Add read-only `scripts/skill-instruction-audit.py` for installed skill
   payload drift and dangling source-tree references. Done.
8. Consider `runtime_contracts` in `skill.toml` only after the audit proves the
   repeated clauses are large enough to justify a compiler.

## Non-Goals

- No automatic full-file merging.
- No global overwrite of repo-local `AGENTS.md` or `CLAUDE.md`.
- No unbounded filesystem scan.
- No Claude-only syntax in `AGENTS.md`.
- No assumption that `skills/AGENTS.md` is runtime context for invoked skills.
