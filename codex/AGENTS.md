Shared runtime instructions for repositories using this dot-agent install.

- Treat this file as base runtime context, not project-specific context.
- Follow repository-local instructions in the active workspace when present.
- Keep personal preferences, private context, and risky local overrides out of this shared repo.
- Use the strategic/tactical/disposable lens when making workflow or tooling decisions:
  - Strategic layer: domain expertise, proprietary context/data, judgment, evals, decision loops, trust.
  - Tactical layer: harnesses, skills, workflows, reviews, deterministic helpers that accelerate the strategic layer.
  - Disposable layer: tool-specific tricks likely to be replaced by a Claude/Codex/Hermes release.
- Prefer work that preserves or compounds the strategic layer; keep tactical work migration-ready and avoid over-investing in disposable tricks.
- When creating or materially rewriting a skill in this repo, follow `skills/AGENTS.md` and include the skill composition contract.
