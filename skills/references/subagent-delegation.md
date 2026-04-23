# Subagent Delegation

Use this reference when a parent skill needs role contracts for delegated or
parallel work.

## Gate

Spawn subagents only when the user explicitly asks for subagents, delegation, or
parallel agent work. Otherwise keep the same role separation locally:
investigate, implement, verify.

## Roles

| Role | Owns | Output |
| --- | --- | --- |
| Explorer | Read-only factual investigation | Evidence, confidence, open items |
| Worker / Implementor | Bounded file-scoped edits | Changed paths, verification run, risks |
| Gate / Verifier | Independent validation | Pass/fail findings tied to spec/tasks |

## Parent Duties

- Curate only the context each role needs.
- Keep write scopes disjoint when multiple workers run.
- Reconcile conflicts before writing durable artifacts.
- Do not delegate the immediate blocker when the parent can keep the critical
  path moving locally.
- For decontaminated research, give Explorer approved factual questions or
  source paths, not the desired answer.
