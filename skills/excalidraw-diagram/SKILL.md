---
name: excalidraw-diagram
description: Create and revise Excalidraw diagrams for architecture, workflow, research, planning, and documentation tasks. Use when the user asks for an Excalidraw drawing, visual map, workflow diagram, or a rendered diagram artifact in docs.
argument-hint: <diagram request and optional output path>
disable-model-invocation: true
---

# Excalidraw Diagram

## Composes With

- Parent: user request for a diagram or visual documentation artifact.
- Children: none by default; Explorer subagents only when the user explicitly authorizes parallel research for diagram content.
- Uses format from: none.
- Reads state from: requested docs, code, roadmap/workflow notes, and optional existing `.excalidraw` files.
- Writes through: `.excalidraw` source files and rendered image files in the user-requested workspace.
- Hands off to: none.
- Receives back from: none.

Create diagrams that explain or argue visually, not uniform boxes on a grid.
Every shape should mirror the concept: fan-out for one-to-many, convergence for
aggregation, loops for feedback, lanes for ownership, and timelines for
sequence.

## Workflow

1. Identify the diagram purpose and audience.
2. Choose output paths. Default to `docs/diagrams/<slug>.excalidraw` and
   `docs/diagrams/<slug>.png` in the active repo when the user does not specify.
3. Read only the source material needed to make the diagram accurate.
4. Create or update the `.excalidraw` source.
5. Render PNG with `scripts/render-excalidraw.sh`.
6. Inspect the PNG visually.
7. Fix layout, text clipping, overlaps, weak hierarchy, or unclear arrows.
8. Rerender until the PNG is readable.
9. When embedding in Markdown, link the PNG only.

## Delivery Contract

- The user-facing deliverable is the human-readable PNG.
- In final responses, list or link only rendered `.png` paths.
- Do not include `.excalidraw` paths, raw Excalidraw JSON, or other editable
  source in the final answer.
- Keep adjacent `.excalidraw` files for durability and future edits, but treat
  them as internal implementation artifacts in normal handoffs.

## Renderer

Use the bundled wrapper:

```bash
~/.dot-agent/skills/excalidraw-diagram/scripts/render-excalidraw.sh \
  docs/diagrams/example.excalidraw \
  docs/diagrams/example.png
```

The wrapper installs the upstream renderer into
`~/.dot-agent/state/tools/excalidraw-diagram-skill/` on first use, then runs its
Playwright-based render pipeline. This keeps third-party code and dependency
caches out of tracked dot-agent source.

The renderer is pinned to the tested upstream commit documented in
`references/upstream-renderer.md`. Read that file before changing renderer setup
behavior or updating the pin.

## Artifact Rules

- Treat `.excalidraw` as the editable source of truth for durable diagrams.
- Treat `.png` as a rendered artifact for docs and review.
- Present the PNG, not the source, in human-facing reading order.
- Track the PNG when a tracked Markdown doc embeds it.
- Keep generated dependency state under `~/.dot-agent/state/tools/`, not under
  `skills/`.
- Do not vendor external renderer code into this repo unless the licensing and
  maintenance decision is explicit.

## Design Rules

- Keep labels short and readable at documentation scale.
- Prefer spatial grouping over long explanatory text.
- Use color semantically and sparingly.
- Make arrows explain ownership or data/control flow; avoid decorative arrows.
- Avoid text overlaps, clipped titles, and unlabeled transitions.
- For workflow maps, show control surfaces, state files, and handoff points.
