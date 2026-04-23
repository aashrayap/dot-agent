---
status: approved
feature: simplify-agent-skill-system
---

# Design: simplify-agent-skill-system

## Relevant Principles

- Keep the always-on human protocol thinner than the skill system. It should
  shape communication, not force every task into the same packet.
- Preserve `This Session Focus` as the first slot because it anchors why the
  session exists and current state.
- Keep `Next Actions` as a first-class slot because Ash uses it to steer the
  next turn quickly.
- Make user-direction questions explicit when the next best step depends on
  Ash's preference.
- Keep the skill composability contract constant; do not make it dynamic just
  because the human-facing response protocol becomes dynamic.
- Improve and compose before deleting.

## Decisions

### D1. Thin the Human Response Contract into three primary slots

Decision: replace the fixed seven-slot default packet with a thinner adaptive
packet:

1. `This Session Focus`
2. `Result`
3. `Next Actions`

`Result` may include concise `Visual`, `Gate`, and `Details` information when
they matter. These become nested content or short sentences, not mandatory
top-level sections for every non-trivial task.

Options considered:

- Keep current fixed packet: reliable but too heavy.
- Remove the contract entirely: concise but loses Ash's session receipt.
- Use a three-slot adaptive packet: keeps the useful receipt while reducing
  noise.

Rationale: Ash explicitly wants a cleaner, dynamic protocol while keeping
`This Session Focus` and `Next Actions`. `Result` can carry verification,
visual links, and file links without making every response look like a form.

Affected areas:

- `AGENTS.md`
- `skills/README.md` Human Response Contract section
- `skills/create-agents-md/assets/AGENTS.template.md`
- `skills/create-agents-md/assets/CLAUDE.template.md`

Risks still open:

- If too loose, agents may stop reporting verification or omitted work.
- Needs enough wording that `Result` includes failures/not-done when relevant.

### D2. Make `Ledger` conditional

Decision: `Ledger` should only appear when it prevents loss of state: multiple
user requests, corrections, follow-ups, parked items, or explicit handoff.

Options considered:

- Keep `Ledger` always for non-trivial work.
- Remove `Ledger`.
- Use conditional `Ledger`.

Rationale: Ash asked whether `Ledger` is important. It is high leverage for
multi-request sessions, but it is noise for simple work.

Affected areas:

- `AGENTS.md`
- `skills/README.md`
- instruction templates

Risks still open:

- Agents may omit ledger when a long thread needs it. The contract should say
  "use when state could otherwise disappear."

### D3. Add user-direction questions under `Next Actions`

Decision: `Next Actions` should include concise direction questions when human
choice is needed. Questions should be few, concrete, and answerable by number
or short phrase.

Options considered:

- Separate `Questions` top-level slot.
- Put questions inside `Next Actions`.

Rationale: Ash wants the protocol concise and clean. A separate slot would add
weight; putting questions inside `Next Actions` keeps steering in one place.

Affected areas:

- `AGENTS.md`
- `skills/README.md`
- instruction templates

Risks still open:

- Too many questions can stall work. Contract should prefer reasonable
  assumptions unless user preference is genuinely needed.

### D4. Do not replace the `skills/README.md` contract with only a pointer

Decision: keep a human response contract in `skills/README.md`, but revise it
to match the thinner root protocol rather than replacing it with a pointer.

Options considered:

- Replace duplicated text with a pointer to `AGENTS.md`.
- Keep duplicate text unchanged.
- Keep aligned, shortened text in `skills/README.md`.

Rationale: Ash answered "no" to replacing the skills README contract with a
pointer. The skill catalog should remain useful as a standalone authoring and
review surface, but it should not drift from root protocol.

Affected areas:

- `skills/README.md`
- `AGENTS.md`

Risks still open:

- Two copies can drift. Mitigate by making the wording short and aligned.

### D5. Add `visual-reasoning` as a grouped skill

Decision: create a new grouped `visual-reasoning` skill that composes
`explain`, `compare`, and `excalidraw-diagram`.

Options considered:

- Create a wrapper skill for visual reasoning.
- Document a workflow group and composition path.
- Merge the skills.

Rationale: Ash said visual reasoning should "compose the different skills."
The existing small skills have distinct jobs: `explain` shapes understanding,
`compare` evaluates differences, and `excalidraw-diagram` creates durable
visual artifacts. A grouped skill gives users one entry point for "reason
visually" while preserving the three specialized child skills.

Affected areas:

- `skills/visual-reasoning/SKILL.md`
- `skills/visual-reasoning/skill.toml`
- `skills/README.md`
- current workflow diagram under `docs/diagrams/`
- `compare/SKILL.md`, `explain/SKILL.md`, and `excalidraw-diagram/SKILL.md`
  only if their `Composes With` text should mention the grouped parent.

Risks still open:

- The grouped skill must not duplicate all child instructions. It should route:
  explain for understanding, compare for differences/judgment, and
  excalidraw-diagram for durable artifacts.
- If trigger wording is too broad, it may activate when a direct `explain` or
  `compare` request would be simpler.

### D6. Keep the skill composability contract constant

Decision: do not change the `Composes With` schema during this pass. Gates stay
inside each skill's workflow/rules unless future use shows a repeated gap.

Options considered:

- Add `Gate` or `Human Protocol` rows.
- Keep the current rows.

Rationale: Ash prefers the composability contract to remain constant. Existing
rows already cover owner, child, read/write, and handoff semantics.

Affected areas:

- `skills/AGENTS.md`
- `skills/README.md`
- `skills/references/skill-authoring-contract.md`

Risks still open:

- Gate semantics may remain uneven across skills. Address by improving workflow
  text where needed, not by expanding the schema yet.

## Open Risks

- Adaptive output can become inconsistent if the contract does not name minimum
  obligations: say what changed, what was verified, what remains, and what to
  do next.
- Keeping shortened protocol in both `AGENTS.md` and `skills/README.md` can
  drift. The shorter the repeated text, the lower the drift risk.
- Visual reasoning grouped skill needs a diagram update to make the parent/child
  path obvious.
- Some long skills may still need slimming after protocol changes, but this
  design intentionally avoids deletion-first work.

## File Map

- `AGENTS.md`: thin global human-agent protocol.
- `skills/README.md`: skill catalog, composition groups, aligned short response
  contract, visual reasoning group.
- `skills/visual-reasoning/SKILL.md`: new grouped visual reasoning entrypoint.
- `skills/visual-reasoning/skill.toml`: install manifest for the grouped skill.
- `skills/create-agents-md/assets/AGENTS.template.md`: generated Codex
  instruction template.
- `skills/create-agents-md/assets/CLAUDE.template.md`: generated Claude
  instruction template.
- `docs/diagrams/skill-composability-workflow.excalidraw`: likely diagram
  source to update or supersede.
- `docs/diagrams/skill-composability-workflow.png`: rendered diagram output.
