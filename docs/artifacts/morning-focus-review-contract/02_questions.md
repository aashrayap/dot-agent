---
status: approved
feature: morning-focus-review-contract
---

# Research Questions: Morning Focus Review Contract

## Codebase

- Where do the `morning-sync`, `focus`, and `execution-review` skills currently live, and what files define their behavior?
- What state files does `focus` read and mutate today?
- What local memory/session sources does `execution-review` read for Codex and Claude, and what metadata is available for dates, cwd, tool use, gates, and final results?
- What does `morning-sync` currently read before recommending the day focus?
- Is there an existing helper for "recent sessions by date range" that can be reused instead of adding another scanner?
- What output format constraints do current skills use for morning packets, focus mutations, and execution-review findings?

## Docs

- Which harness docs define the intended relationship between morning sync, focus, daily review, and execution review?
- Which docs define the human response contract fields that morning sync should preserve?
- Is there a documented memory/privacy boundary for reading Codex and Claude session logs?
- Is there already a durable explanation of "chat as receipt" versus artifact creation that should constrain this workflow?

## Patterns

- Do existing day-start or day-end workflows already separate read-only review from roadmap mutation?
- What is the smallest existing pattern for prompting Ash to continue, reprioritize, park, promote, or drop work?
- How do current skills represent incomplete gates, parked work, and repeated threads across days?
- Is there an established table shape for summarizing recent workstreams?
- How expensive is a normal execution-review pass, and is there already a lightweight mode suitable for morning use?

## External

- None expected unless current Codex or Claude runtime docs are needed to locate session memory. Prefer local harness docs first.

## Cross-Ref

- Given recent-session metadata and current roadmap state, how should the workflow deduplicate a work thread that appears in both places?
- What confidence labels are needed when recent session evidence is partial or inferred?
- Which fields belong in the morning contract versus in an optional deeper execution-review artifact?
- What exact boundary keeps `morning-sync` read-first while still letting it hand proposed mutations to `focus`?
- Should the lookback window be fixed at 3 days, configurable, or dynamic based on last successful daily review?
