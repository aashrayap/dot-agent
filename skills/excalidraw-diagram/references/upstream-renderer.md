# Upstream Renderer Notes

This skill uses the public renderer from:

- Repository: `https://github.com/coleam00/excalidraw-diagram-skill`
- Renderer path after clone: `references/render_excalidraw.py`
- Renderer setup:

```bash
cd ~/.dot-agent/state/tools/excalidraw-diagram-skill/references
uv sync
uv run playwright install chromium
```

The upstream renderer expects an Excalidraw JSON file and can write a PNG:

```bash
uv run python render_excalidraw.py input.excalidraw --output output.png
```

Important behavior:

- It uses `uv` and Playwright.
- It installs Chromium through Playwright.
- It renders through a browser template and screenshots SVG output.
- Its HTML template loads Excalidraw from a CDN, so first render may require
  network access.
- Keep the cloned renderer and dependency caches in `~/.dot-agent/state/tools/`.
  Do not commit `.venv/`, browser caches, or upstream cloned source into
  dot-agent unless that is a deliberate vendor decision.
