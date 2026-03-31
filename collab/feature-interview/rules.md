# Comparison Rules

How to generate and maintain `comparison.md` from `ash.md` and `sushant.md`.

## Inputs

- `ash.md` — Ash's feature-interview SKILL.md snapshot
- `sushant.md` — Sushant's feature-interview SKILL.md snapshot

## Output

- `comparison.md` — regenerated from scratch each time; do not hand-edit

## Sections (in order)

| Section | Max lines | Purpose |
|---------|-----------|---------|
| Philosophy | 3 | Core approach difference in one breath |
| Phase Map | table | Side-by-side phase names + what each phase does |
| Key Divergences | 5 items | The differences that actually matter for output quality |
| Shared DNA | 3 items | What both workflows agree on (anchors for merging) |
| Steal List | 3 per person | Concrete things each person should consider adopting |

## Tone

- Concise, no filler, no praise
- Difference-focused — skip anything identical
- Use exact phase/section names from each skill so the reader can cross-reference
- Bullet or table format only — no prose paragraphs

## Regeneration

1. Read both source files in full
2. Apply sections and max lines above
3. Overwrite `comparison.md` completely
4. Do not modify `ash.md` or `sushant.md`

## Versioning

When either source file changes, note the date at the top of `comparison.md`:

```
Last generated: YYYY-MM-DD
Sources: ash.md (hash), sushant.md (hash)
```
