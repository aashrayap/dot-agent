---
description: "What should you remove instead of add? Subtract before you build. Usage: /consider:via-negativa [topic]"
---

Apply via negativa thinking to: $ARGUMENTS (or the current discussion if no topic given).

<objective>
Instead of asking "what should I add?", ask "what should I remove?" Improvement by subtraction. Complexity, features, steps, dependencies, assumptions — what can be eliminated to make the system better?
</objective>

<process>
1. State what you're trying to improve
2. List everything currently present (features, steps, dependencies, assumptions, code, processes)
3. For each: "Would removing this make the system worse, better, or no different?"
4. Identify candidates for removal (better or no different)
5. Check for hidden dependencies before removing
6. Propose the subtracted version
</process>

<output_format>
**Improving:** [what]

**Current inventory:**
| Item | Remove? | Impact of removal |
|------|---------|-------------------|
| ...  | Yes/No  | [better / worse / neutral — why] |

**Remove:**
- [item] — why it's safe and beneficial to cut

**Keep:**
- [item] — why removing it would make things worse

**Subtracted version:**
[What the system/plan/feature looks like after removal]

**Net effect:** [simpler? faster? clearer? what's the win?]
</output_format>

<success_criteria>
- Genuinely considers removing things, not just trimming edges
- Checks for hidden dependencies (removing X breaks Y)
- The subtracted version is concretely described, not vague
- At least one removal is uncomfortable or non-obvious
</success_criteria>
