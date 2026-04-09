---
name: daily-review
description: Analyze the last N hours of Claude Code usage. Fans out one Explore agent per cwd to inspect every non-trivial session, clusters the returned threads into logical projects (a project may span cwds or split within one), then produces a chronological project ribbon, per-project totals, what-went-well/poorly, and concrete skill/workflow adjustments for tomorrow. Invoke with /daily-review.
argument-hint: <hours>
disable-model-invocation: true
---

# Daily Review

The injected setup is intentionally tiny — just the cwds with activity in the window. Everything deeper is fetched on demand.

**Your pipeline:**

1. Fan out one Explore agent per cwd. Each agent inspects every non-trivial session in its slice and reports a structured summary.
2. Cluster the returned threads into logical projects (same cwd may hold multiple projects; different cwds may belong to the same project). **Repos are NOT projects** — a project is a logical unit of work that may span multiple sessions within a single repo or across repos.
3. For each project cluster, call `fetch-last-day-sessions.py --session-ids <ids> --no-turns` once to get aggregate stats (start, end, wall, AI, human, turn count, cwds) for just that cluster.
4. Write the final report: a chronological project ribbon, per-project totals, and skill adjustments.

## Context

!`~/.claude/skills/daily-review/scripts/daily-review-setup.py $1`

The block above injects `FETCH_SCRIPT`, `INSPECT_SCRIPT`, and `WINDOW_HOURS` as **reference labels** (using `~` paths), plus the list of cwds with activity. Nothing is persisted to disk.

## Command protocol (read before calling any script)

The Bash allow-list matches **literal command prefixes**. Every call — from main context *or* subagent — must use one of these exact shapes:

- **Use `~` paths, not absolute paths.** The Bash allow-list uses `~/.claude/…` patterns. If you expand `~` to `/Users/…`, the permission check fails. Always call scripts with their `~/.claude/…` prefix.
- **No pipes, redirects, chaining, or `bash -c` wrapping.** Run the script as the sole command in the Bash call and parse stdout.
- **Never pass `--out`.** These scripts stream to stdout when `--out` is omitted.
- **Project slugs start with `-`**, so `--project` MUST use the `=` form: `--project=<slug>` (not `--project <slug>` — argparse rejects that because it reads the slug as a flag).
- **Exact approved invocations:**
  - `~/.claude/skills/daily-review/scripts/fetch-last-day-sessions.py --hours <N> --project=<slug>` — subagent fan-out; returns full per-turn list
  - `~/.claude/skills/daily-review/scripts/fetch-last-day-sessions.py --hours <N> --session-ids <id1>,<id2>,... --no-turns` — main orchestrator, once per clustered project; returns `day` + `sessions` only (no per-turn dump)
  - `~/.claude/skills/daily-review/scripts/inspect-session.py --session-id <uuid>` — subagent deep-dive

## Your job

### 1. Fan out one Explore agent per project slug (in parallel)

One message, multiple `Agent` calls. Every agent must set:

- `subagent_type: "Explore"`
- `model: "sonnet"`
- thoroughness: "very thorough"

Each agent's prompt must include verbatim:

- **Thoroughness directive**: "Thoroughness: very thorough — read the full prompt, tool sequence, and subagent tree for every non-trivial session in this cwd."
- **Assigned project slug** (exact directory name from the setup listing).
- **The command-protocol constraints above.**
- **Instructions:**
  1. First, run `~/.claude/skills/daily-review/scripts/fetch-last-day-sessions.py --hours <WINDOW_HOURS> --project=<slug>` as a single Bash call (note the `=`, required because slugs start with `-`). Parse stdout as JSON. This returns the real cwd, per-session numeric stats (agent_seconds, human_seconds, turn_count, tool errors, subagent count, parallel activity), and a per-turn list for context.
  2. For every session with `turn_count >= 2`, run `~/.claude/skills/daily-review/scripts/inspect-session.py --session-id <uuid>` as a single Bash call and parse stdout for full prompts, tool sequences with durations, and the subagent tree.
  3. Skip sessions with `turn_count < 2` (one-turn stubs, abandoned openings) — note the count in your report but do not inspect them.
- **Report template** (agent returns in under 500 words):

  ```
  Project slug: <slug>
  cwd: <real cwd from fetch output>
  Sessions inspected: <n>  (stubs skipped: <n>)
  Wall / AI / Human: <hm> / <hm> / <hm>
  Turns: <n>  Tool errors: <n>  Subagents spawned: <n>

  ## Threads within this cwd
  (A thread is one coherent unit of work. Same cwd may hold multiple unrelated
   threads. Split them here — the orchestrator relies on this.)

  ### Thread: <short label>
  - Session UUIDs (full, comma-separated): <full-uuid-1>,<full-uuid-2>
  - Time: HH:MM → HH:MM (<hm> wall)
  - Messages: <n>
  - What happened: <2-3 sentences>
  - Outcome: shipped / in-progress / stuck / abandoned
  - Went well: <specific, cite <full-uuid>:turn>
  - Went poorly: <specific, cite <full-uuid>:turn>

  ## Skills observed
  - /<skill>: <n> invocations, <outcome pattern, cite <full-uuid>:turn>

  ## Subagents observed
  - <agent_type>: <n> runs, <success pattern>

  ## Recommended workflow adjustments
  - <specific, grounded in a cited failure>

  **Never truncate session ids anywhere in the report.** Always emit the full UUID — in the Session UUIDs line and in every `<full-uuid>:turn` citation. The orchestrator and the user both rely on full UUIDs to look up jsonl files directly.
  ```

### 2. Cluster threads into logical projects (in main context)

Read every agent's report. Build the project list:

- A **project** is a logical unit of work. It is **not** a cwd and **not** a repo.
- Start from the threads each agent identified. Each thread already lists its full session UUIDs — pass those verbatim to fetch.
- **Merge** threads across cwds only when prompts clearly show it's the same work (e.g., an MCP server in one repo being tested from another).
- **Keep separate** threads within a single cwd (or single repo) when the agent flagged them as unrelated. A single repo often holds several distinct projects in one day.
- Output of this step is an in-memory mapping: `{project_name: [session_id, ...]}`. Every non-stub session should land in exactly one project.

### 3. Fetch per-project aggregates

For each clustered project, make **one** Bash call:

```
~/.claude/skills/daily-review/scripts/fetch-last-day-sessions.py --hours <WINDOW_HOURS> --session-ids <id1>,<id2>,... --no-turns
```

`--no-turns` is required — the per-turn list is noise for the orchestrator and blows out context. Parse stdout as JSON and read:

- `day.first_prompt_at`, `day.last_activity_at` → project start/end (HH:MM).
- `day.span_seconds` → wall.
- `day.active_seconds` → active.
- `day.agent_seconds` → AI time.
- `day.human_seconds` → human think time.
- `day.turn_idle_seconds` → idle.
- `sessions[]` → cwds (union of `sessions[*].project`), turn counts, per-session wall.

Sort the resulting project list chronologically by `first_prompt_at`.

### 4. Write the report to stdout (don't save unless asked)

```markdown
# Daily Review — <date>

## Project ribbon (chronological)

| # | Time          | Wall  | Project                          | cwd(s)              | Sessions          |
|---|---------------|-------|----------------------------------|---------------------|-------------------|
| 1 | HH:MM → HH:MM | <hm>  | <logical project name>           | <proj1>[, <proj2>]  | <full-uuid>, ...  |
| 2 | HH:MM → HH:MM | <hm>  | <logical project name>           | <proj1>             | <full-uuid>       |
| … |               |       |                                  |                     |                   |

Answers: *at a high level, how did the human spend their time today?*

## Project totals

| Project                          | Wall  | AI    | Human | Idle  | Turns | Sessions |
|----------------------------------|-------|-------|-------|-------|-------|----------|
| <logical project name>           | <hm>  | <hm>  | <hm>  | <hm>  | <n>   | <n>      |
| …                                |       |       |       |       |       |          |
| **Day total**                    | <hm>  | <hm>  | <hm>  | <hm>  | <n>   | <n>      |

## Per-project notes

### <Logical project name>
- cwd(s): <proj1>[, <proj2>]
- Sessions: <full-uuid>, <full-uuid>
- Time: HH:MM → HH:MM (wall <hm>, AI <hm>, human <hm>)

**What happened**: 1–3 sentences.

**What went well**:
- <specific, cite <full-uuid>:turn>

**What went poorly**:
- <specific, cite <full-uuid>:turn>

### <next logical project>
...

## Skill & workflow adjustments for tomorrow
1. **<skill or workflow name>**: <concrete change>. Grounded in: <full-uuid>:turn citation.
2. **<skill or workflow name>**: <concrete change>. Grounded in: <full-uuid>:turn citation.
3. ...
```

## Principles

- **Specific, not generic.** Always name full session UUIDs and turn indices so the user can open the jsonl directly. Never truncate — no 8-char prefixes, no ellipses.
- **One agent per cwd, not per session.** Keep main context lean — subagents swallow the big `inspect-session.py` outputs.
- **Clustering is the LLM's call.** The setup script only knows cwds; logical projects are decided by reading subagent reports. Repos ≠ projects.
- **Every recommendation must cite a failure.** No generic advice like "use more subagents" — ground it in a specific `<full-uuid>:turn`.
- **Always pass `--no-turns` from the main orchestrator.** The orchestrator only needs aggregate `day` + `sessions` per project; per-turn dumps belong in subagents.
- **Re-prompt signals are heuristics, not conclusions.** Read the prompt text before calling something a re-prompt.
