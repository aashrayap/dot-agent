# <Title>: Research Pro Review Brief

## Reviewer Context

You are reviewing a repository change. Assume access to this Markdown packet
only unless the packet explicitly says otherwise. Do not assume filesystem
access. Repo-relative paths in this document are labels for the inline evidence
blocks below. If this packet mentions machine-local or external context, the
relevant facts are included here.

## Review Target And Mode

- Mode: <product/spec critique | architecture/design critique | implementation/PR review |
  migration/risk review | instruction-surface review>
- Remote target: <commit SHA and optional PR URL, tree URL, or compare URL>
- Base/comparison: <base branch, previous commit, or "none">
- Requested scrutiny: <what the reviewer should challenge hardest>

## Access Protocol

1. Confirm whether repo/browser access exists: <repo URL or "packet only">
2. Use `Inline Evidence` as the minimum source of truth. If repo access exists,
   use `Primary Raw URLs` as source of truth for primary files.
3. Treat PR, branch, tree, and blob pages as context only unless they are the
   only published evidence.
4. If any primary raw URL fails, cite the exact URL and stop. Do not fall back
   to stale branch/cache state.

## Source And Access Policy

- Primary evidence: <repo paths and this packet | uploaded files | listed URLs>
- Web/external sources: <not needed | allowed only for listed questions | broad search allowed>
- Non-repo/local context: <none | summarized in Non-Repo Context Included>
- Sensitive context check: <no secrets, API keys, private user data, or
  irrelevant machine-local details included>

## Primary Raw URLs

- <https://raw.githubusercontent.com/<owner>/<repo>/<commit>/<path>>
- <https://raw.githubusercontent.com/<owner>/<repo>/<commit>/<path>>

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

## Inline Evidence

Inline evidence is required for each primary path/area and any other named file
reference that carries review weight so the reviewer can reason without opening
repository files. Include the relevant line range and a short excerpt or
paraphrase plus why it matters to this review.

`<repo-relative-path>` lines `<line-range>`

```text
<insert minimal snippet or paraphrased evidence>
```

Explanation: <why the excerpt is sufficient evidence for the claim>

`<repeat for another path as needed>`

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
