---
status: complete
feature: human-review-surface-contract
---

# Research Questions: human-review-surface-contract

## Codebase

1. Which current root/runtime instruction files exist, and how do they relate:
   root `AGENTS.md`, `codex/AGENTS.md`, and `claude/CLAUDE.md`?
2. Which files currently define skill authoring, runtime setup, composition, and
   human-facing skill guidance?
3. Where does the Excalidraw-specific contract currently live, and is it scoped
   to the callable `excalidraw-diagram` skill plus human README surfaces?
4. Which setup/runtime files would require mandatory code sampling if changed?
5. Which current artifacts already represent repo-level or skill-level diagrams?
6. Which human-presenting skills should declare an explicit diagram-first
   handoff expectation in their own `SKILL.md` files?

## Docs

1. Does the root README provide enough context for human review of harness
   architecture and setup/runtime behavior?
2. Does `skills/README.md` carry the human-facing skill model, including visual
   artifact usage, without polluting agent-facing skill instructions?
3. Does `skills/AGENTS.md` remain a concise agent-facing authoring/setup
   contract?
4. Do current docs define what must be updated when harness behavior changes?
5. Does `skills/README.md` make the human presentation ladder clear: diagram
   first for understanding, text second for drill-down?

## Patterns

1. What should the Codex session itself expose as the final human review surface
   after files and diagrams?
2. Which agent response phases should be considered required in a typed
   Codex-session review pipeline?
3. When should Excalidraw be used to explain session/execution flow versus
   staying with text tables?
4. How should the review ladder classify changes into docs-only, code-sampled,
   and deep-code-review categories?
5. How should execution-review findings feed back into the repo contract without
   turning the human workflow into forensic session analysis?
6. When a skill presents a recommendation, should it create a fresh diagram,
   update an existing diagram, or link to an already-current diagram?
7. Which outputs are exempt from visual-first presentation because they are
   mechanical, transient, or line-specific?

## External

1. Are there external runtime constraints that require a Claude-specific
   `CLAUDE.md` file even if the root `AGENTS.md` is authoritative?
2. Are there current Codex runtime conventions that make the session transcript
   a stable review surface?

## Cross-Ref

1. How should the root repo contract, skill contract, Excalidraw skill, and
   execution-review skill compose without duplicating ownership?
2. Which rapid-fire decisions are still needed before implementing any further
   cleanup?
3. What verification commands prove that the contract, runtime installs,
   diagrams, and session-review behavior remain aligned?
4. How should human-presenting skills call or reference `excalidraw-diagram`
   without making `skills/AGENTS.md` carry Excalidraw-specific policy?
