---
status: implemented
feature: morning-focus-review-contract
---

# Feature Spec: Morning Focus Review Contract

## Goal

Define a merged morning workflow that uses recent Codex and Claude execution memory to show what Ash has actually been working on, then helps Ash decide whether to continue, reprioritize, park, or promote work into the roadmap.

The workflow should preserve clear skill boundaries:

- `morning-sync` frames the day and produces the morning decision contract.
- `execution-review` gathers evidence from recent local agent sessions.
- `focus` mutates the durable roadmap only after Ash chooses.

Target behavior: the morning block always looks at recent Codex and Claude work, emphasizes yesterday, checks older context in decreasing priority, and produces a concise table under `What you've been working on`.

## Users and Workflows

Primary user: Ash, using Codex as the preferred runtime while keeping Claude workflows portable.

### Current Workflow

- `morning-sync` answers "what should happen today?" from current roadmap/state.
- `focus` answers "change the roadmap/focus board now" and writes durable focus state.
- `execution-review` answers "what actually happened in recent Codex/Claude sessions?" and surfaces evidence, drift, and missed gates.

Current gap: the morning decision pass can miss actual recent work if it only reads explicit roadmap state. Execution review knows what happened but is a separate command, so the day-start loop can lack memory of yesterday's unfiled, half-finished, or high-signal sessions.

### Proposed Workflow

Morning focus block:

1. Read roadmap/focus state.
2. Always read recent Codex and Claude session memory.
3. Weight local yesterday as primary, the 2 prior local days as secondary, and the 5 prior local days as tertiary context.
4. Check recent PRs for roadmap/history projects and local git repos touched recently, with high-level diff/status verification.
5. Emit a concise `What you've been working on` table before `Current commitments`.
6. Put inferred work that is not on the roadmap under `User Decides`; do not auto-add it.
7. Ask Ash which focus stream to carry forward. Avoid one bulk "apply all" when multiple projects likely need separate sessions.
8. Only after Ash chooses, route roadmap mutations through `focus` and optionally create one working document that links the important supporting docs.

### Proposed Morning Contract

Required fields:

- `Date`
- `Window`
- `What you've been working on`
- `User Decides`
- `Current commitments`
- `Open gates`
- `Recent PRs`
- `Hermes`
- `Recommended focus`
- `Decision prompt`
- `Roadmap mutations proposed, if a single selected stream is ready`
- `Not changing unless approved`

Candidate table for `What you've been working on`:

| Workstream | Subcategory | Evidence | Last touched | State | Suggested next move |
|---|---|---|---|---|---|
| Broad workstream name | Specific but not tiny slice | high-level source counts / PR status | Yesterday / N days ago | continuing / blocked / drift / done-ish | continue / park / promote / drop |

## Acceptance Criteria

- The workflow clearly states when to prefer `morning-sync` over `focus`.
- The workflow clearly states when to use `execution-review` alone versus as a sub-pass inside morning sync.
- The morning output includes a concise `What you've been working on` table.
- The lookback policy emphasizes local yesterday, then 2 prior days, then 5 prior days.
- The morning packet shows `User Decides` for recent inferred projects not already on the roadmap.
- Recent PRs are nested concisely under related workstreams, with high-level diff/status verification.
- Hermes appears as a tiny status line such as `Hermes: no findings`.
- The workflow separates read-only diagnosis from roadmap mutation.
- The final prompt to Ash offers concrete choices: continue, reprioritize, park, promote, drop, or create a working doc.
- The workflow remains runtime-portable across Codex and Claude memory sources.
- The contract can be implemented as skill changes without adding a new root doc or a second roadmap state system.

## Boundaries

In scope:

- High-level workflow contract for `morning-sync`, `focus`, `execution-review`, and optional Hermes findings.
- Proposed morning output fields.
- Read/write boundaries between diagnosis and roadmap mutation.
- Research questions needed before editing the skills.
- Durable current-vs-proposed diagram.

Out of scope for this planning pass:

- Editing the skills.
- Reading private session logs before the question checkpoint.
- Changing roadmap state.
- Creating a new scheduler or automation.
- Replacing day-end `daily-review`.
- Auto-adding inferred projects to the roadmap.
- Bulk-applying focus changes across multiple projects in one session.

## Risks and Dependencies

- Session memory paths may differ between Codex and Claude runtimes.
- Some useful work may exist only in chat, not durable files, so evidence confidence must be explicit.
- A merged morning command can become too heavy if execution review is always full-depth.
- `focus` must remain the write gate; otherwise morning sync becomes a hidden roadmap mutator.
- Claude and Codex surfaces may use different naming for sessions, gates, or outcomes.
- The contract should not expose private local paths beyond what Ash expects in local harness output.
