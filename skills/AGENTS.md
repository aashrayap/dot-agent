# Skills Directory Instructions

This directory is the source of truth for shared Claude and Codex skills.

## Composition Contract

Every retained skill must declare how it composes with the rest of the harness.
Add a `## Composes With` section near the top of each `SKILL.md` when creating
or materially rewriting a skill.

Use this structure:

```markdown
## Composes With

- Parent:
- Children:
- Uses format from:
- Reads state from:
- Writes through:
- Hands off to:
- Receives back from:
```

Fill unused rows with `none`. Keep entries concrete: name the skill, state file,
helper script, or artifact path.

Composition types:

- **Uses format**: parent owns the final output; child contributes presentation
  or structure. Example: `compare` uses `explain` visual modes.
- **Routes next**: parent decides which control surface should handle the next
  step. Example: `morning-sync` routes to `focus`, `projects`, or `idea`.
- **Hands off ownership**: child owns the next workflow. Example: `idea` hands
  code-grounded planning to `spec-new-feature`.
- **Reads state**: reader observes another surface's state but does not mutate it
  directly. Example: `morning-sync` reads `roadmap.md` and active projects.
- **Writes through**: a skill changes another surface only through that surface's
  helper scripts or documented mutation rules. Example: `execution-review`
  drains completed roadmap rows through `focus`/`projects` helpers.
- **Returns state**: a deep workflow reports delivery reality back to a durable
  owner. Example: `spec-new-feature` returns PRs, pivots, and follow-ups to
  `projects`.

## Ownership Rules

- `roadmap.md` is the daily operating board.
- `idea` owns idea artifacts under `~/.dot-agent/state/ideas/`.
- `projects` is a thin durable bridge for work that outgrows the roadmap.
- `spec-new-feature` owns deep code-grounded planning and implementation
  artifacts.
- `execution-review` owns review reports and closure recommendations, but writes
  daily/project state only through the owning surfaces.

Do not add a new top-level skill when an existing owner can compose it as a mode,
format dependency, handoff, or helper.
