---
name: compare-skills
description: Compare two skills side-by-side to find divergences and cross-pollination opportunities
disable-model-invocation: true
---

# Compare Skills

**Trigger**: `/compare-skills <skill-a> <skill-b>`

Arguments are skill directory names from `skills/` (e.g., `/compare-skills feature-interview qa`). Also accepts full paths to external SKILL.md files.

## Protocol

1. **Resolve inputs** — load both SKILL.md files. If a name matches a `skills/<name>/SKILL.md`, use that. Otherwise treat as a file path.
2. **Generate comparison** — apply the output format below from scratch. No caching, no incremental updates.
3. **Output to conversation** — render inline. Do not write a file unless explicitly asked.

## Output Format

```
Last compared: YYYY-MM-DD
Sources: <skill-a> (line count), <skill-b> (line count)
```

### Sections (in order)

| Section | Max items | Purpose |
|---------|-----------|---------|
| Philosophy | 3 lines | Core approach difference in one breath |
| Phase/Step Map | table | Side-by-side phase names + what each does |
| Key Divergences | 5 | Differences that actually matter for output quality |
| Shared DNA | 3 | What both workflows agree on (anchors for merging) |
| Steal List | 3 per skill | Concrete things each skill should consider adopting from the other |

### Tone

- Concise, no filler, no praise
- Difference-focused — skip anything identical
- Use exact phase/section names from each skill for cross-reference
- Bullet or table format only — no prose paragraphs
