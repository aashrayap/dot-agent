---
status: draft
feature: simplify-agent-skill-system
---

# Research: simplify-agent-skill-system

## Flagged Items

- F1. `AGENTS.md` currently contains a fixed packet contract, but Ash wants the
  protocol thinner and dynamic by task, skill, and latest human message.
  Evidence: `AGENTS.md` defines fixed slots; Ash answered "yes but I want to
  thin the protocol and think how it needs to be dynamic." Confidence: high.
  Conflict: fixed packet improves reliability, but can add weight to small
  tasks.
- F2. The repo already has a strict skill composability contract. The problem is
  not absence of contract; it is how that contract relates to global
  human-agent communication and how consistently workflow groups expose it.
  Evidence: `skills/AGENTS.md`, `skills/README.md`, and every repo
  `skills/*/SKILL.md` has `## Composes With`. Confidence: high.
- F3. `skills/README.md` duplicates the Human Response Contract from
  `AGENTS.md`. This may help skill authors, but it creates a second source of
  truth for human-facing packet rules. Confidence: high.
- F4. Deletion should not be a near-term research focus. Ash explicitly shifted
  the goal toward improving contracts and workflow grouping first. Confidence:
  high.

## Findings

### Codebase

#### C1. Agent instructions define a global human-agent protocol

Answer: root `AGENTS.md` is a compact always-on protocol file. It defines the
harness purpose, fixed Human Response Contract, operating loop,
planning/coding/review norms, and progressive disclosure links.

Evidence:

- `AGENTS.md` is 86 lines.
- It says final packets for non-trivial work should include `This Session
  Focus`, `Result`, `Visual`, `Gate`, `Ledger`, `Next Actions`, and `Details`.
- It says `Visual` is always a slot, ledger tracks captured/done/not
  done/parked, chat is the receipt unless durable artifacts are needed, and
  every request should be mapped before final response.
- `docs/harness-runtime-reference.md` says root `AGENTS.md` is base runtime
  context, not project-specific context.

Confidence: high.

Conflicts: no repo fact conflict. Human preference now asks for dynamic packet
behavior rather than a rigid slot set for all non-trivial work.

Open item: define which packet parts are mandatory always, conditional, or
skill-owned.

#### C2. Skill composability contract already exists and is broad

Answer: the repo already requires every retained skill to have a strict
`## Composes With` section. The schema is stable across all 15 repo skills:
`Parent`, `Children`, `Uses format from`, `Reads state from`, `Writes through`,
`Hands off to`, and `Receives back from`.

Evidence:

- `skills/AGENTS.md` says every retained skill needs strict `## Composes With`.
- `skills/README.md` defines the schema and explains each relationship.
- `skills/references/skill-authoring-contract.md` repeats the same source-only
  authoring contract.
- `rg` found `## Composes With` in all top-level repo skills:
  `caveman`, `compare`, `create-agents-md`, `daily-review`,
  `excalidraw-diagram`, `execution-review`, `explain`, `focus`,
  `handoff-research-pro`, `idea`, `init-epic`, `morning-sync`, `review`,
  `spec-new-feature`, and `wiki`.

Confidence: high.

Conflicts: no schema conflict found. Some skills are much longer than others,
especially `idea` at 562 lines, which may make the contract harder to see.

Open item: decide whether contract stays exactly as-is or gains a lightweight
`Gate`/`Human Protocol` row without making every skill heavier.

#### C3. Installed Codex skills mirror repo skills, with system/runtime extras

Answer: `~/.codex/skills` contains the repo skills plus system and runtime
skills. Repo skills are source-of-truth in `skills/`; Codex installed copies are
generated payloads.

Evidence:

- Repo has 15 top-level skills under `skills/*/SKILL.md`.
- Installed Codex skills include those same names plus `.system` skills
  (`imagegen`, `openai-docs`, `plugin-creator`, `skill-creator`,
  `skill-installer`) and `codex-primary-runtime` skills (`slides`,
  `spreadsheets`).
- `docs/harness-runtime-reference.md` says runtime homes are install targets,
  not sources of truth.
- `skills/README.md` says Claude receives symlinks while Codex receives copied
  payloads, so setup must run after skill edits.

Confidence: high.

Conflicts: none.

Open item: later design should separate source cleanup from installed runtime
drift checks.

#### C4. Priority workflows match existing composition groups

Answer: Ash's priority list maps cleanly onto two existing hubs and one utility
cluster.

Evidence:

- Daily loop: `morning-sync` has children `focus`, `idea`,
  `spec-new-feature`; `focus` writes roadmap state; `daily-review` drains
  completed rows through `focus`.
- Idea-to-PR: `idea` hands code-grounded planning to `spec-new-feature`;
  `spec-new-feature` hands off to `focus`, `review`, or `daily-review`;
  `handoff-research-pro` packages external review gates; `review` owns code
  review.
- Visual reasoning: `explain` leads with visual structure; `compare` borrows
  `explain` formats and can hand off to `excalidraw-diagram`;
  `excalidraw-diagram` owns durable `.excalidraw` and PNG artifacts.

Confidence: high.

Conflicts: none.

Open item: name and document workflow groups without turning small utilities
into one large skill.

#### C5. Current docs already identify ownership surfaces

Answer: `skills/README.md` is the current catalog and composition reference. It
defines default owners: `focus` for roadmap, `idea` for ideas,
`spec-new-feature` for feature artifacts, `daily-review` for day-end review,
`execution-review` for forensic session reports, `create-agents-md` for
agent-instruction files, and `handoff-research-pro` for external review
packets.

Evidence:

- `skills/README.md` "Default ownership" table.
- `docs/harness-runtime-reference.md` source-of-truth and setup contracts.
- `skills/AGENTS.md` authoring loop.

Confidence: high.

Conflicts: the Human Response Contract is described in both `AGENTS.md` and
`skills/README.md`, so ownership of that contract is not fully clean.

Open item: decide whether `skills/README.md` should link to `AGENTS.md` for
human protocol and reserve local text for skill-specific presentation notes.

### Docs

#### D1. Existing progressive disclosure policy fits Ash's goal

Answer: repo docs already favor small always-on files plus deeper docs loaded
only when needed.

Evidence:

- `AGENTS.md` says "Pull deeper harness facts only when the current task needs
  them."
- `skills/AGENTS.md` says keep `SKILL.md` lean and move setup notes, schemas,
  examples, and variants into `references/`, `scripts/`, `assets/`, or
  `shared/`.
- `skills/references/skill-authoring-contract.md` says `skills/AGENTS.md` is
  source-only author-time policy and any rule needed while using a skill must
  live in the selected entrypoint or explicitly loaded supporting files.

Confidence: high.

Conflicts: several runtime-facing skills still contain substantial policy and
format details in their entrypoints. This may be warranted, but should be
checked during design.

Open item: identify which skill entrypoints are too long because they contain
reference material rather than invocation-critical workflow.

#### D2. Prior artifacts reinforce daily-loop ownership

Answer: existing research artifacts already concluded that `morning-sync`
should orchestrate day-start synthesis, `focus` should own roadmap mutation,
and `execution-review` should remain forensic.

Evidence:

- `docs/artifacts/morning-focus-review-contract/03_research.md` says
  `morning-sync` should not become `execution-review`; it should use lightweight
  evidence intake and suggest `focus` actions.
- The same artifact says `focus` owns `roadmap.md` and writes through
  `skills/focus/scripts/roadmap.py`.
- `docs/artifacts/human-review-surface-contract/03_research.md` says normal
  daily output should avoid raw project/session internals.

Confidence: high.

Conflicts: none for ownership. Open design remains how dynamic final packets
should look for daily-loop tasks.

### Patterns

#### P1. `AGENTS.md` is best treated as human-agent protocol plus universal harness rules

Answer: local and external evidence align: always-on instruction files should
stay concise, universal, and high leverage. They should not absorb every
task-specific playbook.

Evidence:

- Local: root `AGENTS.md` is short, always-on, and points to deeper docs.
- HumanLayer "Writing a good CLAUDE.md" says `CLAUDE.md`/`AGENTS.md` is the
  file that enters every conversation and should be concise, universal, and
  manually considered line by line:
  https://www.humanlayer.dev/blog/writing-a-good-claude-md
- HumanLayer "Skill Issue" says overstuffed system prompts burn instruction
  budget; skills solve this through progressive disclosure:
  https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents
- LogRocket frames `AGENTS.md` as broad/persistent map and skills as narrower
  repeatable expertise:
  https://blog.logrocket.com/context-engineering-for-ides-agents-md-agent-skills/

Confidence: high.

Conflicts: external advice focuses mostly on codebase onboarding, while this
repo uses `AGENTS.md` as a personal human-agent protocol. Mapping is
directionally strong but not one-to-one.

Open item: define "ultra high leverage" global rules for Ash beyond generic
repo onboarding.

#### P2. Skills should remain composable modules, not hidden subprotocols

Answer: skills are the right home for repeatable task playbooks, artifact
ownership, helper scripts, and workflow-specific entry/exit behavior. The
constant composition contract is consistent with both local design and external
skill architecture.

Evidence:

- Local: strict `Composes With` schema and ownership map.
- Anthropic Claude Code docs say skills load only when relevant and are for
  repeated playbooks/procedures rather than always-on files:
  https://code.claude.com/docs/en/skills
- Anthropic skills blog describes three-tier loading: metadata, `SKILL.md`, and
  larger reference files on demand:
  https://claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work
- Anthropic best practices say refine skills through real usage, watch missed
  connections, overreliance, and ignored files:
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Confidence: high.

Conflicts: Codex and Claude do not have identical skill/runtime behavior, so
repo design must preserve portability rather than adopting Claude-only
frontmatter features as the core contract.

Open item: decide how much of Claude's newer skill features should be reflected
in source docs versus kept runtime-specific.

#### P3. Dynamic human-facing protocol should be a routing rule, not many packet variants

Answer: evidence supports a stable global protocol that can choose a response
shape dynamically, rather than each skill inventing its own final response
rules.

Evidence:

- Ash wants the human response protocol to be dynamic by task/skill/type/latest
  message, while keeping the skill composability contract constant.
- OpenAI Agents SDK docs distinguish manager composition, handoffs, dynamic
  instructions, lifecycle hooks, and guardrails:
  https://openai.github.io/openai-agents-js/guides/agents/
- LangGraph HITL docs model dynamic pauses with serialized state and resumption:
  https://docs.langchain.com/oss/python/langgraph/interrupts
- MCP elicitation defines structured accept/decline/cancel user responses and
  client UI duties:
  https://modelcontextprotocol.io/specification/draft/client/elicitation

Confidence: medium-high.

Conflicts: repo implementation is instruction files, not an SDK runtime. The
pattern must be adapted as language-level protocol, not over-modeled as code.

Open item: define a small dynamic packet ladder: tiny command/status,
single-file mechanical work, review findings, planning/research, workflow
decision, multi-artifact work.

### External

#### E1. HumanLayer emphasizes structured human contact, pause/resume, and state

Answer: HumanLayer sources treat human involvement as structured workflow
state, not merely conversational prose.

Evidence:

- HumanLayer SDK documentation says high-stakes functions need deterministic
  human oversight, with `require_approval` and `human_as_tool` as primitives:
  https://github.com/humanlayer/humanlayer/blob/main/humanlayer.md
- HumanLayer 12 Factor Agents says owning control flow allows pausing for human
  input, waiting on long tasks, serializing context, and optimizing "what
  happened so far":
  https://www.humanlayer.dev/blog/12-factor-agents
- HumanLayer 12 Factor Agents says tool-like human contact gives clearer
  instructions, supports agent-to-human initialization, multiple humans,
  agent-to-agent extension, and durable workflows.
- Subagent research found HumanLayer docs use `run_id` for workflow execution
  and `call_id` for individual function/human-contact calls, plus synchronous
  and async request/response patterns.

Confidence: high.

Conflicts: some older HumanLayer SDK pages are marked legacy or were removed
from current docs. Architectural patterns remain consistent across current
HumanLayer blog/README material.

Open item: whether dot-agent needs structured local state for human protocol,
or whether chat-plus-artifacts is enough.

#### E2. OpenAI and LangChain both separate orchestration from specialist work

Answer: current agent frameworks distinguish a global orchestrator/manager from
specialists/handoffs. They also warn that guardrails and context do not
automatically apply everywhere; boundaries must be explicit.

Evidence:

- OpenAI Agents SDK docs: manager-as-tools keeps one conversation owner;
  handoffs transfer conversation ownership to a specialist:
  https://openai.github.io/openai-agents-js/guides/agents/
- OpenAI handoffs docs recommend including handoff information in agents so LLMs
  understand routing:
  https://openai.github.io/openai-agents-python/handoffs/
- OpenAI guardrails docs say input/output guardrails run at workflow boundaries,
  while tool guardrails are needed around each custom function tool:
  https://openai.github.io/openai-agents-js/guides/guardrails/
- LangChain handoffs docs advise using a single agent with middleware for most
  handoff cases and only using multiple subgraphs when bespoke agent
  implementations are needed:
  https://docs.langchain.com/oss/javascript/langchain/multi-agent/handoffs

Confidence: high.

Conflicts: SDK guidance is about programmatic agents; dot-agent uses markdown
contracts and local scripts. Still relevant for deciding where global versus
specialist behavior belongs.

Open item: decide whether `AGENTS.md` is the "manager" layer and skills are
"specialists", or whether `morning-sync`/`spec-new-feature` are workflow
managers under a thinner global protocol.

#### E3. MCP elicitation gives a useful language for human input states

Answer: MCP elicitation distinguishes accept, decline, and cancel; requires
clear UI about who is asking and why; and separates ordinary structured input
from sensitive URL-mode flows.

Evidence:

- MCP elicitation spec:
  https://modelcontextprotocol.io/specification/draft/client/elicitation
- It says clients must let users review/modify form responses, decline/cancel,
  and see which server is requesting information.
- It prohibits sensitive secrets in form-mode elicitation and requires URL mode
  for sensitive interactions.

Confidence: medium-high.

Conflicts: the spec is draft and not all clients support it equally.

Open item: whether Ash's local human-agent protocol should borrow the
accept/decline/cancel vocabulary for follow-up actions and checkpoint answers.

### Cross-Ref

#### X1. `AGENTS.md` and `SKILL.md` should relate as protocol and modules

Answer: evidence supports this relationship:

- `AGENTS.md`: universal human-agent communication, latest-message handling,
  approval/pause norms, ledger/gate expectations, durable-artifact policy,
  source-of-truth setup principles, and progressive disclosure pointers.
- `SKILL.md`: trigger, constant composition contract, state/artifact ownership,
  workflow steps, helper scripts, child-skill usage, skill-specific gates, and
  handoff targets.

Evidence:

- Ash explicitly identified these two "very important pieces."
- Local docs already separate root runtime context from skill authoring and
  skill ownership.
- External sources converge on lean always-on context plus task-loaded
  procedures.

Confidence: high.

Conflict: `skills/README.md` currently repeats global human response details.

Open item: design exact wording and source-of-truth links.

#### X2. Keep constant skill composition contract; make human response protocol adaptive

Answer: Ash's answers and the evidence support a fixed `Composes With`
contract, while the human-facing response protocol should adapt by task shape.

Evidence:

- Ash answered that the skill contract should remain constant.
- Ash answered that the human-facing response protocol does not need to remain
  constant.
- Local `Composes With` schema is already successfully deployed across skills.
- External sources favor progressive disclosure and concise always-on
  protocols.

Confidence: high.

Conflict: dynamic response behavior could make outputs less predictable if not
bounded by a small ladder.

Open item: choose the ladder.

#### X3. Workflow grouping should improve discoverability without merging small skills

Answer: the named clusters are already composable; the improvement target is
catalog/navigation and contract clarity, not collapsing skills.

Evidence:

- Daily loop maps to `morning-sync` -> `focus` -> `daily-review`.
- Idea-to-PR maps to `idea` -> `spec-new-feature` -> `review` /
  `handoff-research-pro` / `focus`.
- Visual reasoning maps to `explain`, `compare`, and `excalidraw-diagram`.
- Ash said "kind of small pieces all over the place" and then named the
  priority skills.

Confidence: high.

Conflicts: no evidence that merging would improve behavior; external sources
generally favor narrower, relevant context.

Open item: decide catalog shape and whether groups need a lightweight top-level
index, examples, or wrappers.

## Patterns Found

- Lean always-on protocol, rich task-loaded skill.
- Constant skill composability schema; dynamic human packet ladder.
- Workflow hubs with small utilities: `focus` hub for daily loop,
  `spec-new-feature` hub for code-grounded planning, visual reasoning group for
  `explain`/`compare`/`excalidraw-diagram`.
- Write-through ownership: skills that mutate shared state should do so through
  owner scripts or documented paths.
- Human input as structured checkpoint: ask, approve, decline, cancel, resume.
- Context control as first-class design: keep universal instructions short,
  push reference detail into linked docs/files/scripts, and use subagents for
  bounded evidence gathering when explicitly authorized.

## Core Docs Summary

- `AGENTS.md`: current root human-agent protocol and always-on harness rules.
- `docs/harness-runtime-reference.md`: source-of-truth, runtime install, and
  setup contracts.
- `skills/AGENTS.md`: source-tree skill authoring contract.
- `skills/README.md`: skill catalog, composability schema, ownership map,
  diagrams, human presentation notes, external review gate, subagent roles.
- `skills/references/skill-authoring-contract.md`: detailed authoring schema,
  source-only policy, setup contract, ownership map, subagent roles.
- HumanLayer sources: concise `CLAUDE.md`/`AGENTS.md`, progressive disclosure,
  skills for reusable knowledge/tools, subagents for context control, structured
  human contact and pause/resume.
- Anthropic sources: skills as dynamically loaded folders with frontmatter,
  instructions, scripts, and reference files; iterative refinement based on
  observed use.
- OpenAI/LangChain/MCP sources: explicit handoffs, state, guardrails,
  interrupts, and structured human input states.

## Open Questions

1. Which response packet slots are mandatory across all non-trivial work, and
   which should become conditional by task shape?
2. Should the dynamic human response protocol be documented as a compact ladder
   in `AGENTS.md`, or as a separate linked reference with only a summary in
   `AGENTS.md`?
3. Should `skills/README.md` continue to duplicate the Human Response Contract,
   or should it point to `AGENTS.md` and only describe skill-specific
   presentation expectations?
4. Should `Composes With` gain a `Gate` or `Human protocol` row, or should
   gate behavior remain inside each skill's workflow text?
5. How should "visual reasoning" be presented: a named workflow group in
   `skills/README.md`, an index section, or a lightweight wrapper skill?
6. Should rare but valuable small skills stay visible as utilities, or be
   nested under workflow groups in docs while remaining separate runtime skills?
7. Which prior diagrams should be treated as current source-of-truth versus
   historical artifact before design updates them?
