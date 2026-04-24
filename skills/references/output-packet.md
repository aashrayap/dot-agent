# Output Packet

Use this reference when a skill needs Ash-facing delivery shape without
restating the full contract.

## Shape

For non-trivial work, final responses use:

```markdown
This Session Focus
<why this session started; optional current state>

Result
<what changed, what was verified, what remains open, key links>

Next Actions
1. <concrete next step>
```

Add `Ledger` only when state would otherwise disappear: multiple requests,
corrections, follow-ups, parked items, or handoff-heavy work.

## Rules

- Keep chat as the receipt unless durable state is needed for roadmap, PR,
  docs, review, or handoff continuity.
- Put visuals, verification gates, unknowns, and detail links inside `Result`
  when they matter.
- Map each user request to done, not done, or parked before final response.
- Make `Next Actions` concrete and answerable by number or short phrase when
  human direction is useful.
