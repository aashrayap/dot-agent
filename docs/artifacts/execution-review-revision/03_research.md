---
status: in-progress
feature: execution-review-revision
---

# Research: Execution Review Revision

## Flagged Items

1. **Hermes “self-improvement” is real but narrower than the marketing copy suggests.**
   The current upstream implementation clearly supports memory nudges, skill nudges, and background review forks, but not a synchronous “pause every N tool calls and rewrite yourself” loop.
   **Confidence:** High

2. **Mainline Hermes does not natively ingest Codex or Claude Code session stores.**
   I found auth reuse/import from `~/.codex/auth.json` and Claude credential files, plus orchestration skills for Codex and Claude Code CLIs, but no current reader for `.codex` session/history stores or `~/.claude/projects/`.
   **Confidence:** High

3. **The current execution-review stack is materially under-scoped for the requested revision.**
   It is Codex-only, manual, and markdown-oriented; it has no durable normalized store, no Claude adapter, and no Hermes analysis layer.
   **Confidence:** High

4. **The repo strongly prefers mutable state under `~/.dot-agent/state/`, but the current execution-review implementation still hardcodes `~/.codex/`.**
   This is a real constraint for the rewrite because shared skill guidance explicitly says not to hardcode runtime homes inside shared skill content.
   **Confidence:** High

5. **Identity splitting (`ash` vs `sushant`) has no active implementation backing in the current repo.**
   It exists only in the obsolete `look` artifacts and not in current state/config/skill wiring.
   **Confidence:** Medium

## Findings

### Codebase

#### Q1: What exactly does the current `execution-review` skill do today?

**Answer**

The current skill is a **Codex-only retrospective**. It runs a three-step workflow:

1. enumerate recent top-level Codex threads
2. summarize them into aggregate signals
3. inspect a small subset of threads manually before writing a markdown report

It does not define structured persistent history beyond “save the report under `~/.dot-agent/state/collab/execution-reviews/` if the user asks.”

**Evidence**

- `skills/execution-review/skill.toml` targets only `["codex"]`.
- `skills/execution-review/codex/SKILL.md` describes only `~/.codex/state_*.sqlite` and `~/.codex/sessions/**`.
- The output contract is markdown-only daily/weekly reviews.
- Save behavior is optional and path-based, not a machine-readable history protocol.

**Confidence:** High

**Conflicts**

- None in the current repo.

**Open items**

- None; current behavior is clear.

#### Q2: Which parts of the current Codex parser are reusable as the foundation of the revision?

**Answer**

The current parser already has a strong reusable split:

- `select_threads()` for source selection
- `summarize_thread()` for per-thread event reduction
- `build_aggregate()` for cross-thread rollups

The aggregate layer is reusable as-is in shape. The thread selector and summarizer are tied to Codex schemas and would need runtime adapters.

**Evidence**

- `skills/execution-review/scripts/codex_sessions.py` defines:
  - `select_threads()`
  - `summarize_thread()`
  - `build_aggregate()`
- `fetch-codex-sessions.py` composes those functions into a report payload.
- `inspect-codex-session.py` builds a judge input layer on top of the same summary structure.

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Whether the revised normalized schema should preserve the current summary shape exactly or evolve it.

#### Q3: What additional raw signals are already available in local Codex artifacts that the current review skill does not use?

**Answer**

The current parser already extracts more than the current markdown review contract uses. Available but underused signals include:

- `model`, `reasoning_effort`, `approval_mode`, `sandbox_policy`
- `agent_nickname`, `agent_role`, `agent_path`
- `commentary_messages` vs `final_messages`
- raw `tool_counts`
- `skill_mentions` from user messages using `$skill` syntax
- per-command timelines and command events when `include_timeline=True`
- `source_info` for spawned/subagent threads

These are useful for workflow analysis and “missed opportunity” scoring, but they are not reflected in the current daily/weekly report contract.

**Evidence**

- `skills/execution-review/scripts/codex_sessions.py`
  - thread columns include model/reasoning/approval/sandbox/agent fields
  - `SKILL_RE` extracts `$skill` mentions
  - summary output includes `tool_counts`, `skill_mentions`, commentary/final counts, source metadata
  - optional timeline and command event capture

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Presentation-quality analysis still lacks a designed extraction strategy even though assistant text is present in rollouts.

#### Q4: What local patterns already exist in `~/.dot-agent` for durable state, append-only history, and review/audit loops?

**Answer**

The repo already uses several durable-state patterns:

- **Append-only history log:** `compare` writes `~/.dot-agent/state/collab/compare-history.md`
- **Active-state + audit log:** `projects` stores `project.md` plus `AUDIT_LOG.md`
- **Immutable raw log + rewritten structured sections:** `idea`
- **Generated state + append-only log:** `wiki` uses `index.md`, generated index files, and append-only `log.md`

This means the repo has strong precedent for:

- mutable state under `~/.dot-agent/state/`
- append-only logs
- human-readable audit trails

It does **not** currently show one settled convention for machine-readable analytics history.

**Evidence**

- `README.md` and `skills/README.md` define mutable state boundaries under `~/.dot-agent/state/`
- `skills/compare/SKILL.md`
- `skills/projects/SKILL.md`
- `skills/wiki/SKILL.md`
- `skills/idea/SKILL.md`

**Confidence:** High

**Conflicts**

- The repo favors markdown logs today, while the obsolete execution-review draft favored JSONL.

**Open items**

- Whether the revised review system should use markdown, JSONL, SQLite/DuckDB, or a layered combination.

#### Q5: What parts of the current `look` planning artifacts are still useful evidence, and which assumptions should be treated as stale?

**Answer**

The `look` artifacts remain useful for **raw research findings**, especially:

- Claude Code session schema discoveries
- runtime dual-target skill layout precedent
- wiki frontmatter and state-location research
- the clean three-layer parser reuse observation

The stale or unsupported assumptions are:

- that identity splitting is already justified or configured
- that the old spec should remain the active plan
- that the prior scorecard and data model are still the right frame

The `look` plan is also stale procedurally: project tracking was scaffolded but not maintained, and `04_design.md` / `05_tasks.md` were never turned into a current executable plan.

**Evidence**

- `docs/artifacts/look/01_spec.md`
- `docs/artifacts/look/02_questions.md`
- `docs/artifacts/look/03_research.md`
- `~/.dot-agent/state/projects/look/project.md`
- `~/.dot-agent/state/projects/look/AUDIT_LOG.md`

**Confidence:** High

**Conflicts**

- The schema research is still useful; the planning layer is not.

**Open items**

- None; the current status is clear.

### Docs

#### Q6: What does the local repo documentation say about config ownership, runtime homes, and mutable state boundaries?

**Answer**

The repo documentation is explicit:

- `~/.dot-agent` is the versioned source of truth
- live runtimes remain under `~/.claude` and `~/.codex`
- shared mutable outputs belong under `~/.dot-agent/state/`
- shared skills should not hardcode runtime-home assumptions

This creates a real constraint for the rewrite: a shared execution-review system should be rooted in `~/.dot-agent/state/`, even if it reads runtime artifacts from `~/.codex` and `~/.claude`.

**Evidence**

- `README.md`
- `skills/README.md`

**Confidence:** High

**Conflicts**

- Current execution-review scripts still hardcode `CODEX_HOME = ~/.codex`.

**Open items**

- Whether the rewrite should parameterize runtime-home discovery via env/config or keep direct reads localized to adapter code.

#### Q7: What does the local wiki skill require from generated outputs?

**Answer**

The wiki skill expects:

- YAML frontmatter on generated pages
- `title`, `tags`, `sources`, `created`, `updated`
- immutable `raw/`
- updates to `index.md`
- rebuild of generated graph files via `/wiki rebuild-index`
- append-only `log.md`

For query outputs, it uses `outputs/`; for source-derived content it uses `sources/`. The execution-review rewrite should therefore produce **wiki-ready markdown** but not assume direct auto-write.

**Evidence**

- `skills/wiki/SKILL.md`

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Whether review outputs should be treated as `sources/` entries, `outputs/` entries, or both depending on workflow.

### Patterns

#### Q8: What dimensions should the revised review score, and which of them can be evidence-backed from current telemetry?

**Answer**

Current telemetry strongly supports evidence-backed scoring for:

- focus / fragmentation
- verification discipline
- command failure recurrence
- some grounding signals
- skill usage signals and missed opportunities

Current telemetry weakly supports direct scoring of:

- response presentation quality

because presentation quality requires inspecting assistant text and follow-up patterns, not just counts. The telemetry is present, but the current parser does not yet formalize presentation signals.

**Evidence**

- Current Codex parser captures commands, tool usage, thread depth, failures, commentary/final message counts, first user message, and assistant text in rollouts.
- Current execution-review rubric is evidence-based and limited to dimensions the parser already supports.

**Confidence:** Medium

**Conflicts**

- None at the telemetry layer.

**Open items**

- How to define presentation-quality evidence rigorously enough for scoring without drifting into vibes.

#### Q9: What is the right boundary between deterministic evidence collection and higher-level interpretation?

**Answer**

The current repo strongly separates:

- deterministic extract/aggregate code
- narrative interpretation in skills/docs

This is visible in the current execution-review pattern and in other repo patterns like `wiki` and `compare`. The evidence boundary should remain code-first; higher-level interpretation should remain a secondary layer.

**Evidence**

- `skills/execution-review/scripts/*.py` handle extraction; `codex/SKILL.md` handles narrative judgment.
- `compare` and `wiki` similarly separate state/data handling from interpretive output.

**Confidence:** High

**Conflicts**

- None.

**Open items**

- How far to let Hermes participate in interpretation before it becomes an implementation dependency rather than an optional analysis layer.

#### Q10: What is the right durability model for the revised review loop?

**Answer**

Current evidence does **not** show one settled durability model in the repo for this class of analytics problem.

What is established:

- shared mutable state belongs under `~/.dot-agent/state/`
- append-only logs are common
- generated machine-readable graph state is acceptable in the wiki

What is not yet established:

- whether analytics history should live in JSONL, SQLite/DuckDB, markdown, or a hybrid layout

So the durability model remains unresolved at research time.

**Evidence**

- `README.md`
- `skills/README.md`
- `skills/compare/SKILL.md`
- `skills/wiki/SKILL.md`
- obsolete `look` spec used JSONL, but that was not implemented

**Confidence:** High

**Conflicts**

- Markdown-log precedent vs machine-readable-history requirement.

**Open items**

- Exact storage model is a design decision.

#### Q11: Is identity splitting (`ash` vs `sushant`) still justified in the revised design?

**Answer**

No current repo evidence justifies identity splitting as a required first-class feature. It appears only in the obsolete `look` artifacts, and there is no active mapping config or current state model that depends on it.

This makes identity splitting a product/design question, not a discovered repo constraint.

**Evidence**

- `docs/artifacts/look/01_spec.md` and `02_questions.md` assume identity splitting.
- No current execution-review code, repo config, or shared state defines identity mapping.

**Confidence:** Medium

**Conflicts**

- User intent may still want identity segmentation even if the repo does not currently support it.

**Open items**

- Whether to keep identity splitting in scope for the rewrite or defer it.

### External

#### Q12: How does Hermes actually natively self-improve in the current upstream implementation?

**Answer**

Hermes natively self-improves through a combination of:

- built-in memory review nudges
- built-in skill creation/update nudges
- a background review fork that can write memory or patch/create skills after a turn
- persistent session search over Hermes-native history
- optional external memory providers like Honcho for deeper user modeling

The current mainline implementation does **not** show DSPy-based runtime self-improvement as part of the core agent loop. DSPy appears in the repo as a skill/catalog entry, not as the native self-improvement engine.

**Evidence**

- `run_agent.py`
  - `_MEMORY_REVIEW_PROMPT`
  - `_SKILL_REVIEW_PROMPT`
  - `_COMBINED_REVIEW_PROMPT`
  - `_spawn_background_review()`
  - `_memory_nudge_interval`
  - `_skill_nudge_interval`
- `cli-config.yaml.example`
  - `memory.nudge_interval`
  - `skills.creation_nudge_interval`
- `website/docs/user-guide/features/skills.md`
- `tools/skill_manager_tool.py`
- `rg "dspy"` in the repo returns the packaged `skills/mlops/research/dspy/` skill and catalog docs, not core runtime logic

**Confidence:** High

**Conflicts**

- README/docs language is broader and more marketable than the precise runtime mechanics.

**Open items**

- None for the current upstream repo; the mechanism is clear enough.

#### Q13: What does Hermes persist natively, and how different is that from what `.codex` exposes?

**Answer**

Hermes persists several first-class layers:

- `~/.hermes/state.db` with `sessions`, `messages`, and `messages_fts`
- gateway transcripts under `~/.hermes/sessions/`
- built-in curated memory files (`MEMORY.md`, `USER.md`)
- agent-managed skills under `~/.hermes/skills/`
- optional external memory provider state/config

By contrast, `.codex` primarily exposes:

- session/state SQLite
- rollout JSONL
- config/rules/instructions

This means Hermes has a native “memory + procedural memory + searchable session history” stack, while `.codex` primarily provides “history + config + runtime metadata.”

**Evidence**

- `hermes_state.py`
- `website/docs/user-guide/features/memory.md`
- `website/docs/user-guide/features/skills.md`
- `website/docs/user-guide/sessions.md`
- `agent/memory_provider.py`
- current local Codex parser and execution-review skill

**Confidence:** High

**Conflicts**

- None.

**Open items**

- None.

#### Q14: Can Hermes natively ingest Codex or Claude Code history, or would that require a custom adapter layer?

**Answer**

It would require a **custom adapter layer**.

In the current upstream repo, the Codex- and Claude-related integrations I found are:

- auth reuse/import
- orchestration skills that call Codex or Claude Code CLIs

I did not find a native reader for:

- `.codex` session/state history stores
- `~/.claude/projects/`
- `sessions-index.json`

**Evidence**

- Repo-wide search shows Codex integration centered on `~/.codex/auth.json`
- Claude integration centers on credentials and orchestration skills
- No search hits indicating native ingest of `.codex` session databases or Claude project-session stores

**Confidence:** High

**Conflicts**

- None in current mainline.

**Open items**

- Whether an MCP wrapper, direct file parser, or normalized review input is the better adapter target.

#### Q15: What parts of Hermes are relevant to this feature versus attractive but orthogonal?

**Answer**

**Directly relevant:**

- memory/skill review loop
- `skill_manage`
- `session_search`
- `state.db` session storage model
- optional memory providers like Honcho
- cron if scheduled retrospectives matter

**Mostly orthogonal to execution review itself:**

- broad messaging gateway/platform adapters
- voice mode
- provider/auth machinery
- Codex/Claude orchestration skills
- DSPy skill catalog entry

These may be useful for a broader “agent OS” setup, but they are not required to solve the execution-review rewrite.

**Evidence**

- `website/docs/index.md`
- `website/docs/user-guide/features/skills.md`
- `website/docs/user-guide/features/memory.md`
- `website/docs/user-guide/sessions.md`
- `website/docs/reference/skills-catalog.md`

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Whether scheduled Hermes-driven retrospectives should be in the first ship or later.

### Cross-Ref

#### Q16: What is the cleanest architecture for combining execution-review evidence with Hermes findings?

**Answer**

Current evidence supports only one clean conclusion at research time:

- Hermes should not be treated as the native source of truth for Codex/Claude telemetry
- any combination requires an adapter boundary between execution-review evidence and Hermes analysis

The current repo does not already provide that integration, so this remains a design problem rather than an existing pattern.

**Evidence**

- Local execution-review is evidence-driven and Codex-native
- Hermes is Hermes-session-native
- no native ingestion bridge exists

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Exact handoff format between the two layers.

#### Q17: If Hermes is used as a suggestion or optimization layer, what mutation boundary is safe?

**Answer**

The current repo strongly suggests a conservative mutation boundary:

- tracked source lives in `~/.dot-agent`
- mutable outputs live under `~/.dot-agent/state/`
- risky local overrides should stay out of tracked shared config

There is no current repo pattern that justifies autonomous mutation of tracked shared runtime config by a secondary analysis layer. Safe mutation policy remains an open design choice, but current repo guidance leans toward **reviewed changes**, not silent auto-patching.

**Evidence**

- `README.md`
- `skills/README.md`
- absence of any current execution-review auto-mutation flow

**Confidence:** High

**Conflicts**

- Hermes itself can manage its own skills internally, but that does not imply safe auto-patching of this repo’s tracked shared config.

**Open items**

- Whether the rewrite should allow proposal generation only, proposal + diff generation, or reviewed patch application.

#### Q18: What is the smallest shippable revision that materially improves the current system?

**Answer**

The smallest gap between current state and requested outcome is:

- add Claude Code ingestion
- add durable review history
- widen the score/evidence model beyond the current Codex-only markdown review

Hermes-native analysis is additive beyond that gap, not the minimum requirement to materially improve the current system.

This is not yet a design decision; it is simply what the evidence says is missing today.

**Evidence**

- Current execution-review is Codex-only
- no durable structured history exists
- Hermes integration currently requires a custom adapter

**Confidence:** High

**Conflicts**

- None.

**Open items**

- Which of those gaps should ship in the first milestone versus later phases.

## Patterns Found

1. **Evidence-first extractors are already a strong local pattern.**
   Python scripts handle deterministic source reduction; SKILL docs handle narrative judgment.

2. **State separation is a repo invariant.**
   Tracked shared instructions live in `~/.dot-agent`; mutable artifacts live in `~/.dot-agent/state/`.

3. **Hermes natively optimizes future behavior, not foreign runtimes’ raw history.**
   Its self-improvement mechanisms operate on Hermes sessions, Hermes memory, and Hermes skills.

4. **Hermes memory and skills are distinct layers.**
   Memory is factual and always-on; skills are procedural and on-demand.

5. **The main Hermes repo does not currently use DSPy as its native self-improvement engine.**
   DSPy exists as a research skill, not as the main loop’s learning mechanism.

## Core Docs Summary

### Local repo docs

- `README.md` / `skills/README.md`
  - define `~/.dot-agent` as source of truth
  - define `~/.dot-agent/state/` as mutable state boundary
  - discourage hardcoded runtime-home paths in shared skill content

### Hermes docs

- `website/docs/index.md`
  - markets Hermes as a self-improving agent
- `website/docs/user-guide/features/skills.md`
  - defines skills as procedural memory
  - confirms agent-managed skills through `skill_manage`
- `website/docs/user-guide/features/memory.md`
  - defines built-in memory files and `session_search`
- `website/docs/user-guide/features/honcho.md`
  - defines Honcho as an external memory provider plugin
- `website/docs/user-guide/sessions.md`
  - defines SQLite-backed Hermes session storage with FTS5

## Open Questions

1. **How should response presentation quality be operationalized?**
   The raw text is available, but the scoring model is not yet defined.

2. **Should identity splitting stay in scope?**
   Current repo evidence does not justify it, but user intent may.

3. **What durability layout should the rewrite use?**
   Markdown logs, JSONL, SQLite/DuckDB, or a layered combination remain unresolved.

4. **What is the Hermes handoff format?**
   There is no existing integration; the bridge shape is a design decision.
