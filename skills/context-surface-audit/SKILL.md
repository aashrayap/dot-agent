---
name: context-surface-audit
description: >
  Audit dot-agent context surfaces for word counts, duplicate anchors, runtime
  install shape, and skill manifest schema coverage without reading transcript
  content.
argument-hint: [--format text|json]
disable-model-invocation: true
---

# Context Surface Audit

## Composes With

- Parent: harness reduction, context budget review, or structural audit request.
- Children: `execution-review` only when a structural finding needs forensic session evidence.
- Uses format from: none.
- Reads state from: dot-agent source files, skill manifests, and runtime install metadata.
- Writes through: none by default; caller may paste output into feature artifacts or PR notes.
- Hands off to: `execution-review` for transcript/session diagnosis; `spec-new-feature` for implementation tasks.
- Receives back from: `execution-review` when forensic evidence changes structural recommendations.

Run `scripts/context-surface-audit.py` when the user asks where context is
leaking, whether skill manifests are covered, or whether runtime installs match
the source/runtime ownership model.

The audit is privacy-preserving. It reports counts, anchors, paths, symlink/copy
shape, and manifest coverage; it does not dump transcript text or inspect raw
chat content.

## Commands

```bash
python3 skills/context-surface-audit/scripts/context-surface-audit.py --format text
python3 skills/context-surface-audit/scripts/context-surface-audit.py --format json
```

## Output

- root/default instruction word counts
- largest skill instruction files
- duplicate anchor counts
- runtime surface symlink/copy status
- skill manifest schema coverage
- warnings that identify likely reduction targets
