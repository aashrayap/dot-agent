# Upstream Renderer Notes

This skill uses the public renderer from:

- Repository: `https://github.com/coleam00/excalidraw-diagram-skill`
- Default pinned commit: `8646fcc9f74f38539c6cdb4c969723336a96ddcd`
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
- The pinned renderer commit controls the wrapper and template revision, but
  the CDN asset itself is still a residual determinism risk. Full offline
  determinism requires a deliberate vendor step for the browser asset.
- `render-excalidraw.sh` checks out the pinned commit by default so durable
  docs do not drift with upstream `main`.
- To test a different renderer revision, set `EXCALIDRAW_RENDERER_REF` to a
  commit, tag, or branch name before running the wrapper. Update this reference
  file when changing the default pin.
- Keep the cloned renderer and dependency caches in `~/.dot-agent/state/tools/`.
  Do not commit `.venv/`, browser caches, or upstream cloned source into
  dot-agent unless that is a deliberate vendor decision.
