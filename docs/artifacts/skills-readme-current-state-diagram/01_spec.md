---
status: approved
feature: skills-readme-current-state-diagram
---

# Feature Spec: skills-readme-current-state-diagram

## Goal

Replace the `/skills` README diagram with a current-state, human-readable view of
the dot-agent skill setup. The diagram should summarize the operational shape
already described below it and show the high-level workflows people actually use
now.

## Users and Workflows

- Ash reads the README to understand how the harness, runtimes, setup, and
  skills relate today.
- A future agent reads the README to orient before changing shared skills.
- A reviewer checks that the diagram matches current files and does not preserve
  stale published-vs-target workflow framing.

## Acceptance Criteria

- Diagram in the skills README no longer centers old published/current-target
  workflow language.
- Diagram shows current setup, runtime targets, install path, skill authoring
  contract, and high-level workflows.
- Existing surrounding README content remains intact except for diagram-related
  updates needed for consistency.
- Repository e2e/setup verification passes or any failure is explained with
  concrete evidence.
- Root `AGENTS.md` and Claude runtime `CLAUDE.md` put the Human Response
  Contract at the top.
- Pull request is created for the change.

## Boundaries

- Scope is documentation, rendered diagram artifacts, and supporting planning
  artifacts only.
- Do not alter runtime behavior, setup semantics, or skill files unless current
  README text requires a small consistency fix.
- Do not touch unrelated local changes.

## Risks and Dependencies

- README may contain Mermaid or other diagram syntax with constraints that need
  to stay renderable.
- Repo setup/e2e command may install into runtime homes; verify current e2e
  expectation before running.
- Existing uncommitted local changes may be user-owned and must not be included
  unless directly required.
