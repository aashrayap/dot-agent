# <Title>: Research Pro Review Brief

## Reviewer Context

You are reviewing a repository change. Assume access to the remote Git
repository and this Markdown packet only. Use repo-relative paths when opening
files. If this packet mentions machine-local or external context, the relevant
facts are included here.

## Review Target And Mode

- Mode: <product/spec critique | architecture/design critique | implementation/PR review |
  migration/risk review | instruction-surface review>
- Remote target: <branch, commit SHA, PR URL, tree URL, or compare URL>
- Base/comparison: <base branch, previous commit, or "none">
- Requested scrutiny: <what the reviewer should challenge hardest>

## Source And Access Policy

- Primary evidence: <repo paths and this packet | uploaded files | listed URLs>
- Web/external sources: <not needed | allowed only for listed questions | broad search allowed>
- Non-repo/local context: <none | summarized in Non-Repo Context Included>
- Sensitive context check: <no secrets, API keys, private user data, or
  irrelevant machine-local details included>

## Goal

- <Why this work started>
- <What outcome the change is trying to produce>

## General Direction

1. <Main design/workflow direction>
2. <Secondary direction or constraint>
3. <Important preservation rule>

## Files To Review

Primary starting points, not hard boundaries:

- `<repo-relative-path>`
- `<repo-relative-path>`

## Review Breadth

Inspect adjacent code, docs, tests, manifests, scripts, or related workflow
surfaces when needed to validate whether the change fits the repo. Keep broader
findings tied back to the stated goal.

## Non-Repo Context Included

- <Important local/runtime/external fact that the reviewer cannot fetch from the remote repo>
- <Omit this section if no non-repo context matters>

## Assumptions And Blind Spots

Assumptions to falsify:

1. <Assumption> - <current evidence> - <what would disprove it>
2. <Assumption> - <current evidence> - <what would disprove it>

Reviewer blind spots:

- <Example: no access to local runtime homes, untracked files, browser tabs, or
  private state unless summarized here>
- <Example: validation output is quoted from this packet, not independently rerun>

## What Changed

`<path-or-area>`

- <Behavioral or structural change>
- <Why it matters>

`<path-or-area>`

- <Behavioral or structural change>
- <Why it matters>

## Validation Already Run

- `<command>`: <passed/failed/not run and reason>

## Known Out Of Scope

- <Unrelated dirty files, unrelated warnings, or intentionally excluded work>

## Findings Intake Plan

Returned findings should be triaged into:

- fix now: <where accepted blocking/high findings should land>
- backlog: <roadmap row, feature task, or handoff doc for accepted later work>
- local verification: <findings that need tests, runtime checks, or repo commands>
- reject with reason: <where rejected findings should be recorded, if anywhere>

## Review Tasks

Please review for:

1. <Concrete risk or question>
2. <Concrete risk or question>
3. <Concrete risk or question>

## Bonus Scope

If time allows, briefly audit nearby or repo-wide surfaces for similar issues.
Keep bonus findings separate from primary review findings.

## Desired Reviewer Output

Lead with findings. For each finding include:

- severity: blocker, high, medium, low
- file/path
- issue
- why it matters
- suggested fix

If there are no blocking findings, say that explicitly and list polish
suggestions separately.
