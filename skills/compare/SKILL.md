---
name: compare
description: Compare two skills, workflows, configs, or any structured files side-by-side. Produces a concise diff-focused analysis.
---

# Compare

Generic comparison of two files. Works on skills, CLAUDE.mds, configs, workflows — anything structured.

## Commands

```
/compare <file1> <file2>                  — compare two files, output to stdout
/compare <file1> <file2> -o <output>      — compare and write to a file
```

## Process

1. Read both files in full.
2. Identify the type of content (skill, config, markdown doc, code) and adapt section headers accordingly.
3. Generate comparison using the output format below.
4. If `-o` specified, write to that path. Otherwise, output directly.
5. Append an entry to the history file (see History section).

## Output Format

```markdown
Last compared: YYYY-MM-DD
Sources: <file1 basename>, <file2 basename>

# Compare: <file1 name> vs <file2 name>

## Philosophy
- **<name1>**: [1 line — core approach]
- **<name2>**: [1 line — core approach]

## Structure Map
[Table — side-by-side sections/phases/blocks, one column per file. Skip identical rows.]

## Key Divergences
[Max 5 items. The differences that actually matter for output quality. Each item: what differs, why it matters.]

## Shared DNA
[Max 3 items. What both agree on — anchors for merging.]

## Steal List
[Max 3 per side. Concrete things each should consider adopting from the other.]
```

## History

The skill maintains a history log at `~/.claude/collab/compare-history.md`. This file tracks every comparison run and how the inputs evolved over time.

**On every run**, append an entry to the history file (create it if it doesn't exist):

```markdown
## YYYY-MM-DD — <file1 basename> vs <file2 basename>

**Delta from last run** (same pair): [first run | no changes | summary of what moved]
**Key divergences**: [count]
**Steal list items**: [count adopted since last run] / [count total]
```

**Rules for history entries:**
- Match pairs by basenames — if the same two files were compared before, diff against that prior entry
- "Delta from last run" captures what changed between iterations: new sections added, divergences resolved, steal list items adopted
- If a steal list item from a prior run now appears in the adopter's file, mark it as adopted
- Keep entries append-only — never edit or remove old entries
- If the history file exceeds 50 entries, archive entries older than 6 months to `~/.claude/collab/compare-history-archive.md`

## Rules

- Concise, no filler, no praise
- Difference-focused — skip anything identical
- Use exact section/phase/function names from each file so the reader can cross-reference
- Bullet or table format only — no prose paragraphs
- Max lines per section: Philosophy 1 per file, Key Divergences 5, Shared DNA 3, Steal List 3 per side
- Infer names from file basenames (e.g., `ash.md` → "Ash", `bryce-feature-interview.md` → "Bryce")
