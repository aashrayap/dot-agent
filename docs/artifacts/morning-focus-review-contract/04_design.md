---
status: implemented
feature: morning-focus-review-contract
---

# Design: Morning Focus Review Contract

## Relevant Principles

- Keep roadmap central. Recent session memory can inform the morning decision, but it does not become a second control plane.
- Compose existing owners. `morning-sync` orchestrates, `execution-review` supplies evidence, and `focus` writes roadmap state.
- Reality leads plan. The morning packet shows `What you've been working on` before `Current commitments`.
- Hide implementation machinery. Session IDs, subagent mechanics, raw PR review internals, and runtime transcript anchors stay out of normal morning output.
- Separate multi-project carry-forward. Ash often copies packets into different sessions, so the morning output should avoid a single bulk apply path.
- Use Hermes as secondary signal only. Hermes findings can annotate the evidence bundle, but raw Codex/Claude telemetry remains source of truth.

## Decisions

### D1. Morning-sync becomes roadmap plus lightweight recent-work intake

`morning-sync` should always read:

- `~/.dot-agent/state/collab/roadmap.md`
- recent Codex and Claude normalized session evidence
- recent execution-review history when useful
- optional Hermes findings

It should not render a full execution-review report during the normal path. The intake is a compression layer for day-start decisions.

### D2. Lookback uses local calendar priority bands

Use local-day bands, not only a rolling `3d` window:

- Primary: yesterday
- Secondary: 2 prior local days
- Tertiary: 5 prior local days

The output should make this visible as a `Window` field and use the bands to weight rows, not to flood the packet.

### D3. Workstreams are broad with useful subcategories

`What you've been working on` should use broad workstream rows with one moderate-granularity subcategory. Avoid one row per session and avoid vague repo-only labels.

Table shape:

| Workstream | Subcategory | Evidence | Last touched | State | Suggested next move |
|---|---|---|---|---|---|
| `dot-agent` | morning focus contract | sessions + PRs + docs | yesterday | continuing | carry forward |

Evidence should be high-level: source counts, project/repo names, PR status, and important doc links. Session IDs stay out unless Ash asks for audit.

### D4. User Decides holds inferred work outside the roadmap

Morning-sync should scan both:

- projects/workstreams already in `roadmap.md`
- projects inferred from recent session history and recently touched local git repos

If a recent workstream is not in roadmap, show it under `User Decides` and do not auto-add it.

### D5. Recent PRs are verified in parallel but presented nested and concise

Implementation may verify PR status/diffs in parallel per project/workstream. The user-facing output should not mention subagents. It should show concise nested PR rows under the related workstream:

```markdown
- dot-agent
  - PR #12: title, status, high-level diff area, risk/gate
```

Diff inspection stays high-level: files/areas changed, open review status, CI/check state when available, and obvious blockers. Do not expand into full code review unless Ash asks.

### D6. Focus writes happen only after explicit selected-stream approval

For one selected workstream, morning-sync may ask whether to apply focus changes now and then route through `focus`.

For multiple projects, do not offer `Apply all`. Ask Ash which stream(s) to carry forward and prepare copy-paste friendly working packets.

### D7. Working documents are approval-only and one-per-morning where possible

Do not create working docs during the normal read-only morning scan. If Ash approves carrying work forward, create one concise working document when it helps coordinate multiple sessions.

Preferred shape:

- `Goal`
- `Evidence`
- `Important Docs`
- `Next Step`
- `Gate`

Preferred storage is still open. Bias away from bloating `docs/`; likely candidates are `~/.dot-agent/state/collab/morning/YYYY-MM-DD.md` for local daily operating packets or repo-local docs only when the packet must be durable/reviewable.

### D8. Hermes is a tiny status line

Show Hermes as a tiny line, e.g.:

```text
Hermes: no findings
```

If findings exist, show count and short title only. Deeper Hermes content belongs in execution-review.

### D9. Dot-agent owns this feature artifact

The canonical planning packet lives in:

```text
~/.dot-agent/docs/artifacts/morning-focus-review-contract/
```

The misplaced `semi-stocks-2` packet should be deleted after this dot-agent packet exists.

## Open Risks

- Always reading recent sessions may slow a normal morning call unless the summarizer is lightweight.
- The line between "lightweight intake" and "forensic execution-review" can drift unless the output contract forbids session IDs and deep scoring.
- Local-day banding needs careful timezone handling.
- Recent PR verification across all local git repos touched recently may be expensive or noisy without a repo cap.
- Working documents can become another docs pile if created by default; they must stay approval-only.
- Hermes has a consumer bridge but no observed producer output, so the status line may remain `no findings` until a producer is configured.

## File Map

Implemented surfaces:

- `skills/morning-sync/SKILL.md` — contract update, output format, routing rules.
- `skills/morning-sync/scripts/morning-sync-setup.sh` — reports recent-work and working-doc helper paths.
- `skills/morning-sync/scripts/recent-work-summary.py` — lightweight recent-work summarizer.
- `skills/execution-review/SKILL.md` — clarifies lightweight evidence intake handoff to `morning-sync` without changing forensic ownership.
- `skills/focus/SKILL.md` — clarifies selected-stream writes and working-doc handoff.
- `skills/focus/scripts/morning-working-doc.py` — approval-only local morning working-doc writer.
- `docs/artifacts/morning-focus-review-contract/` — planning artifacts.
- `docs/diagrams/morning-focus-review-current-vs-proposed.png` — human-facing visual.
