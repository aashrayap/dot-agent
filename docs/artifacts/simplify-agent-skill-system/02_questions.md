---
status: approved
feature: simplify-agent-skill-system
---

# Research Questions: simplify-agent-skill-system

## Codebase

- Which files currently define agent instructions for dot-agent, and which
  instruction blocks are exact or near duplicates?
- Which parts of `AGENTS.md` currently define the human-agent communication
  protocol: final packet shape, ledger, visual requirement, gates, operating
  loop, and escalation rules?
- Which skill directories exist in the repo, and which installed skill copies
  exist under runtime homes?
- Which setup, audit, manifest, or install scripts define the source-of-truth
  path from repo skill files to installed runtime skill files?
- Which skills reference, compose with, or hand off to other skills in their
  `SKILL.md` files?
- Which skills already contain an explicit composability contract such as
  `Composes With`, reads-from, writes-through, hands-off-to, receives-back-from,
  or response contract sections?
- Which skills are referenced by roadmap rows, idea artifacts, handoff docs,
  diagrams, automation prompts, README files, or other durable state?
- Which skills have recent local session evidence, modified artifacts, or
  generated outputs that indicate active use?
- Which skills have overlapping responsibilities, repeated response contracts,
  repeated artifact paths, or copied workflow rules?
- Which skills participate in the priority cluster Ash named:
  `morning-sync`, roadmap/focus work, `focus`, `spec-new-feature`, `idea`,
  `handoff-research-pro`, and `review`?
- Which skills participate in the small-piece visual/thinking cluster Ash named:
  `explain`, `compare`, and `excalidraw-diagram`?
- Which skills contain user-authored judgment that is not present elsewhere?

## Docs

- What does the harness runtime reference say about source-of-truth locations,
  install targets, and setup/audit expectations?
- What does `skills/AGENTS.md` require when materially rewriting skills?
- What does `skills/README.md` currently present as the official skill catalog
  and workflow grouping?
- Which diagrams currently document skill workflows, and do they match the
  repo skill set?
- Which docs mention Codex vs Claude behavior, and are any instructions
  contradictory or stale?
- Which docs define or imply what belongs in global agent instructions versus
  skill-local instructions?
- Which docs explain skill composition well enough for a future agent to choose
  the right entry point without reading every skill?

## Patterns

- What repeated sections or phrases appear across skills and agent instruction
  files, and which repeats are useful contracts versus removable duplication?
- What composition patterns recur across skills: parent/child, handoff,
  reads-state, writes-artifact, or verification gate?
- What should be the minimal common skill composability contract across all
  non-trivial skills?
- Which global human-agent communication rules should remain centralized in
  `AGENTS.md` and referenced by skills instead of copied?
- Which skill-local rules are currently global only because no skill contract
  existed yet?
- Which skills are naturally grouped by one owner workflow rather than existing
  as standalone top-level entry points?
- Which small skills should remain standalone utility modules but be grouped in
  docs through composition examples?
- Which cleanup patterns already exist in the repo for deprecating, migrating,
  or quarantining harness content?
- Which response contracts are global enough to move upward, and which are
  skill-specific enough to stay local?

## External

- Are any current Codex or Claude skill/agent-file conventions relevant enough
  to constrain how source files should be structured?
- Are there current runtime limitations around skill discovery, skill naming,
  nested directories, or installed skill metadata that affect grouping or
  deprecation design?

## Cross-Ref

- How should `AGENTS.md` human-agent protocol and skill composability contracts
  relate so agents know both how to communicate with Ash and how to chain skills
  without duplicating instructions?
- For each candidate skill to improve, group, merge, quarantine, or keep, what
  evidence supports the action across code references, durable artifacts,
  diagrams, and human-stated importance?
- Which skills appear unused by references but still preserve unique judgment
  or rare workflows that should be kept?
- Which duplicated instructions can be removed from one surface because another
  verified surface owns them?
- Which workflow groups would reduce cognitive load without making skills less
  composable: daily loop, idea-to-PR, review/handoff gates, and
  explain/compare/excalidraw?
- What is the safest migration order that preserves behavior after each step?
