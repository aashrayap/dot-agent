# Progressive Disclosure + Handoff Skill: Research Pro Review Brief

## Reviewer Context

You are reviewing a dot-agent repository change. Assume access to the remote Git
repository and this Markdown packet only. Use repo-relative paths when opening
files. Where this packet mentions local/runtime/chat context that is not in the
remote repo, the relevant facts are included below.

This is a final design-quality review for agent instruction surfaces and a new
handoff skill. It is not a broad product review unless you have time for the
bonus scope.

Current working branch during packaging: `main`.

## Review Ref

Remote review is blocked until this local work is published. Before sending
this packet to a remote-only reviewer, create a branch or PR and replace this
section with one of:

- Branch: `<remote-branch-name>`
- Compare URL: `<compare-url>`
- PR URL: `<pull-request-url>`

## Goal

- Refactor always-loaded agent instruction files so they focus on how the agent
  operates across human communication, planning, coding/execution, review,
  verification, and handoff.
- Move setup-heavy, repo-shape-heavy, runtime-specific, and skill-authoring
  details behind progressive-disclosure paths so tokens are spent only when the
  details are needed.
- Update `create-agents-md` so future `AGENTS.md` and `CLAUDE.md` rewrites use
  the same progressive-disclosure approach for both Codex and Claude.
- Add `/handoff-research-pro` as a reusable skill for producing this kind of
  portable external-review packet.

## General Direction

1. Keep always-on instructions short and behavioral.
2. Preserve crucial contracts, especially the human response shape and skill
   composition schema.
3. Move long or conditional details into reference files with clear "read when"
   guidance.
4. Use runtime-native disclosure:
   - Codex `AGENTS.md`: plain Markdown sections and "Read When Needed" links.
   - Claude `CLAUDE.md`: narrow `<important if="...">` blocks for conditional
     guidance.
5. Keep shared facts aligned across Claude and Codex surfaces without forcing
   identical wording.
6. Treat handoff packet "Files To Review" as primary starting points, not hard
   review boundaries.

## Files To Review

Primary starting points, not hard boundaries:

- `AGENTS.md`
- `claude/CLAUDE.md`
- `skills/AGENTS.md`
- `docs/harness-runtime-reference.md`
- `skills/references/skill-authoring-contract.md`
- `skills/create-agents-md/SKILL.md`
- `skills/create-agents-md/codex/SKILL.md`
- `skills/create-agents-md/claude/SKILL.md`
- `skills/create-agents-md/references/progressive-disclosure.md`
- `skills/create-agents-md/assets/AGENTS.template.md`
- `skills/create-agents-md/assets/CLAUDE.template.md`
- `skills/create-agents-md/skill.toml`
- `skills/handoff-research-pro/SKILL.md`
- `skills/handoff-research-pro/assets/research-pro-brief.template.md`
- `skills/handoff-research-pro/skill.toml`
- `skills/README.md`

## Review Breadth

Inspect adjacent code, docs, setup scripts, manifests, skill payload logic, and
existing skill patterns when needed to validate whether the change fits the
repo. In particular, check:

- `setup.sh` skill installation behavior
- `scripts/skill-instruction-audit.py`
- `scripts/repo-instruction-audit.py`
- existing skills under `skills/*/SKILL.md`
- `skills/README.md` if you need current skill architecture context
- `docs/diagrams/` only if visual references matter

Keep broader findings tied back to the stated goals. Separate bonus repo-wide
findings from primary review findings.

## Non-Repo Context Included

- User intent: "all of this in agent md should be progressively disclosed"; the
  main content in `AGENTS.md`, `CLAUDE.md`, and `skills/AGENTS.md` should focus
  on how the agent operates across coding, planning, execution, and human
  communication.
- User intent: details about runtime context, repo shape, setup contract, and
  skill contract should not consume tokens until necessary.
- User intent: `create-agents-md` should become generic for both Claude and
  Codex paths while preserving composition information.
- User intent: the HumanLayer article should inform Claude-specific progressive
  disclosure:
  https://www.humanlayer.dev/blog/stop-claude-from-ignoring-your-claude-md
- Article usage summary: keep foundational Claude guidance visible, but move
  task-specific guidance into narrow `<important if="...">` blocks instead of
  one long always-on `CLAUDE.md`.
- User intent: the `## Composes With` structure/schema is important and should
  remain, but reviewers may suggest improvements that make it clearer, more
  enforceable, or less token-heavy without weakening it.
- User correction for `/handoff-research-pro`: portable does not mean
  repo-relative-only. If important context lives outside the remote repo, the
  handoff must inline the needed facts in the single packet.
- User correction for `/handoff-research-pro`: "Files To Review" should guide
  the reviewer to likely starting points, but must not scope the reviewer too
  narrowly. The reviewer should be free to inspect broader repo context where
  necessary.

## What Changed

`AGENTS.md`

- Opens with repo identity, Codex preference, and short always-on guidance.
- Keeps the human response contract always visible.
- Replaces setup/repo/skill detail with behavioral sections:
  `Operating Loop`, `Planning`, `Coding`, `Review`.
- Adds `Progressive Disclosure` links to deeper reference files.

`claude/CLAUDE.md`

- Stands alone as Claude's global entrypoint instead of only forwarding to
  `AGENTS.md`.
- Keeps response contract and core operating loop always visible.
- Uses narrow `<important if="...">` blocks for:
  - dot-agent runtime/setup changes
  - skill creation or material rewrite
  - improving/translating `AGENTS.md` or `CLAUDE.md`

`skills/AGENTS.md`

- Keeps always-on skill authoring policy short.
- Preserves composition and runtime packaging rules.
- Moves detailed schema, manifest baseline, source-only policy, ownership map,
  and subagent role contracts into `skills/references/skill-authoring-contract.md`.

`docs/harness-runtime-reference.md`

- New progressive-disclosure reference for runtime context, repo shape, setup
  contract, and skill contract.

`skills/references/skill-authoring-contract.md`

- New progressive-disclosure reference for `## Composes With` schema, source-only
  policy, minimum skill shape, manifest baseline, setup contract, ownership map,
  and subagent roles.

`skills/create-agents-md/*`

- Reframes the skill as "Create Agent Instructions" instead of only
  `AGENTS.md`.
- Meaning: it should create, improve, or translate both Codex `AGENTS.md` and
  Claude `CLAUDE.md` surfaces while preserving shared facts in each runtime's
  native format.
- Adds a classification workflow: always-on, conditional, referenced, deleted.
- Adds Claude-specific entrypoint and `CLAUDE.template.md`.
- Updates Codex entrypoint to point to the shared progressive-disclosure
  workflow.
- Adds `references/progressive-disclosure.md`.
- Updates `skill.toml` with `claude_entry = "claude/SKILL.md"`.

`skills/handoff-research-pro/*`

- New skill for creating a single portable Markdown handoff packet for ChatGPT
  Research Pro or another remote-only external reviewer.
- Core metrics include portable, scoped but not boxed in, complete,
  evidence-backed, reviewable, composable, token-aware, handoff-durable, and
  gate-visible.
- Template includes `Review Breadth` and `Non-Repo Context Included` so remote
  reviewers can inspect broader repo surfaces and receive required local facts.

`skills/README.md`

- Updated to describe `create-agents-md` as the owner for dual-runtime
  `AGENTS.md`/`CLAUDE.md` instruction authoring.
- Adds `handoff-research-pro` as the owner for external remote-review packets.
- Clarifies that `handoff-research-pro` should link visuals only when they help
  a remote reviewer understand the change.

## Validation Already Run

- `python3 /Users/ash/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/handoff-research-pro`: passed.
- `git diff --check`: passed after final packet edits.
- `./setup.sh`: passed skill instruction audit.
- Setup reported: 15 skills, 26 runtime payloads, no skill instruction drift.
- Repo instruction audit reported unrelated local warnings for
  `/Users/ash/Documents` and `/Users/ash/Documents/2026/semi-stocks-2`. Treat
  those as out of scope for this review.
- Remote publication: not done at packet time. This packet must include a branch,
  compare URL, or PR URL before another remote-only review.

## Known Out Of Scope

The local worktree also had unrelated pre-existing edits in:

- `claude/settings.json`
- `codex/config.toml`

Do not review those as part of the progressive-disclosure or handoff-skill work
unless they are intentionally included in the remote branch/diff.

The repo-instruction audit warnings for `/Users/ash/Documents` and
`/Users/ash/Documents/2026/semi-stocks-2` come from local workspace discovery,
not this dot-agent change.

No `skills/CLAUDE.md` was added. Reason: setup does not install that path, and
adding a dead instruction surface would create drift risk.

## Review Tasks

Please review for:

1. Does any critical always-needed instruction get hidden too deeply?
2. Are the new "Read When Needed" links discoverable enough for an agent?
3. Are Claude `<important if>` conditions narrow and useful rather than broad?
4. Is Codex `AGENTS.md` free of Claude-only XML and still clear as Markdown?
5. Are skill composition requirements preserved strongly enough?
6. Does `create-agents-md` now genuinely support both Claude and Codex paths?
7. Are there contradictions between root `AGENTS.md`, `claude/CLAUDE.md`,
   `skills/AGENTS.md`, and the new reference docs?
8. Are any repo-relative paths wrong, stale, or too machine-specific for a
   remote-only reviewer or future contributor?
9. Is the split too fragmented, or does it improve token use without making the
   system harder to operate?
10. Does `/handoff-research-pro` encode the right portability rule: inline
    important non-repo facts instead of requiring machine access?
11. Does `/handoff-research-pro` give reviewers enough freedom to inspect
    broader repo context while still giving useful starting points?
12. Does `skills/README.md` now correctly reflect dual-runtime
    `create-agents-md` ownership and the new `handoff-research-pro` owner?

Composability note: the agent composition structure/schema is intentionally
important and should remain. Please verify that the `## Composes With` contract
and related schema definitions are preserved, then suggest improvements only if
they make composition clearer, more enforceable, or less token-heavy without
weakening the contract.

## Bonus Scope

If time allows, briefly audit the rest of the repo for similar
instruction-design problems, stale references, duplicated setup policy, or
places that would benefit from the same progressive-disclosure pattern. Keep
bonus findings separate from the primary review.

## Desired Reviewer Output

Lead with findings. For each finding include:

- severity: blocker, high, medium, low
- file/path
- issue
- why it matters
- suggested fix

If there are no blocking findings, say that explicitly and list polish
suggestions separately. Keep bonus findings in their own section.
