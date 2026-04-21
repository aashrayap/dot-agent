---
status: approved
feature: unified-workflow-morning-sync
---

# Research Questions: unified-workflow-morning-sync

## Codebase

- Where does `morning-sync` force `recent-work-summary.py --skip-prs`, and is
  that unconditional or only part of a fast path?
- What inputs does `recent-work-summary.py` use to classify workstreams,
  subcategories, timestamps, evidence weight, and roadmap membership?
- What thresholds or filters currently suppress old, tiny, smoke-test, or
  low-value sessions from the morning board?
- How can roadmap rows be mapped to repositories for concise PR lookup without
  adding private machine-only state to tracked config?
- Which helper owns roadmap mutation for adding `dot-agent` and how should
  follow-up rows or review summaries be written safely?

## Docs

- What do the current `morning-sync`, `focus`, and `execution-review`
  contracts say about recent PRs, recent-work evidence, and raw session detail?
- Do the harness runtime docs define where repo mappings, local paths, or
  GitHub availability should live?
- Do existing artifact or daily-review docs already define an improvement tally
  pattern?

## Patterns

- How do existing skills distinguish day-start summaries from forensic review
  packets?
- How do existing scripts represent unavailable external signals without
  making the output look empty or misleading?
- How do current roadmap helpers keep updates section-aware and reversible?

## External

- What GitHub access method is available in the Codex desktop runtime for
  repo-level recent PR summaries?
- What failure modes should be expected from PR lookup: no auth, no network,
  repo not installed, rate limit, or no matching user PRs?

## Cross-Ref

- Which recent-work rows in the current morning output came from roadmap rows
  versus inferred session evidence, and which should be visible by default?
- What minimal PR summary would have represented the current `dot-agent` and
  `semi-stocks-2` state without listing every PR?
- What should the normal morning-sync output say when PR lookup is deliberately
  skipped versus attempted and empty?
