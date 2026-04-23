---
name: visual-reasoning
description: Compose explain, compare, and excalidraw-diagram for visual thinking workflows. Use when the user asks to reason visually, explain and compare a system, turn a concept into a reusable visual, or choose between ASCII/table/diagram output.
---

# Visual Reasoning

## Composes With

- Parent: user request for visual reasoning, visual explanation, visual comparison, or reusable visual artifact planning.
- Children: `explain`, `compare`, and `excalidraw-diagram`.
- Uses format from: `explain` for structural visual leads; `compare` for side-by-side and delta judgment; `excalidraw-diagram` for durable rendered diagrams.
- Reads state from: requested files, docs, code, workflows, diagrams, or provided context.
- Writes through: none by default; `excalidraw-diagram` writes `.excalidraw` and `.png` artifacts when a durable visual is needed.
- Hands off to: `explain` for understanding, `compare` for differences/tradeoffs, and `excalidraw-diagram` for durable visual artifacts.
- Receives back from: child skill outputs as the source for the final synthesis.

Use this as the grouped entrypoint when the task needs more than one visual
reasoning move or when the user has not yet chosen the right visual surface.
Keep this skill lean. Do not copy child skill workflows into this file.

## Routing

Choose the smallest child path that satisfies the request:

| User Need | Route | Output Bias |
|-----------|-------|-------------|
| Understand a system, concept, workflow, or code path | `explain` | Structural visual first, then concise prose |
| Compare files, skills, workflows, branches, or designs | `compare` | Side-by-side judgment and deltas |
| Preserve or share a diagram | `excalidraw-diagram` | Editable `.excalidraw` plus rendered PNG |
| Explain then preserve | `explain` -> `excalidraw-diagram` | Explanation shapes the diagram |
| Compare then preserve | `compare` -> `excalidraw-diagram` | Comparison remains analytical source of truth |

## Rules

- Start with the user's actual intent: understanding, comparison, durable
  artifact, or a mix.
- Prefer direct `explain` or `compare` when one child skill is enough.
- Use `excalidraw-diagram` only when a durable artifact is explicitly requested
  or materially useful for workflow, architecture, planning, review, or
  handoff.
- When composing multiple children, keep ownership clear: `compare` owns
  judgments, `explain` owns mental models, and `excalidraw-diagram` owns
  diagram files.
- Keep final responses aligned with the root human response contract.
