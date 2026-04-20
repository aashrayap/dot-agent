# Offline Renderer Notes

This skill previously used the public renderer from:

- Repository: `https://github.com/coleam00/excalidraw-diagram-skill`
- Default pinned commit: `8646fcc9f74f38539c6cdb4c969723336a96ddcd`
- Renderer path after clone: `references/render_excalidraw.py`

That upstream template imported Excalidraw from `https://esm.sh`, so render
success depended on browser network access. That failed in Codex sessions where
network access was disabled.

Current source of truth:

- Renderer script: `skills/excalidraw-diagram/assets/renderer/render_excalidraw.py`
- Browser template: `skills/excalidraw-diagram/assets/renderer/render_template.html`
- Local export bundle: `skills/excalidraw-diagram/assets/renderer/dist/excalidraw-export.bundle.js`
- Bundle source: `skills/excalidraw-diagram/assets/renderer/src/excalidraw-export.js`
- Package pins: `skills/excalidraw-diagram/assets/renderer/package.json` and `package-lock.json`
- Python pins: `skills/excalidraw-diagram/assets/renderer/pyproject.toml` and `uv.lock`
- Runtime state: `~/.dot-agent/state/tools/excalidraw-diagram-renderer/`

Pinned packages:

- `@excalidraw/excalidraw`: `0.18.0`
- `react`: `18.2.0`
- `react-dom`: `18.2.0`
- `esbuild`: `0.28.0`
- `playwright`: `1.56.0`

Important behavior:

- Rendering uses `uv` and Playwright.
- Chromium and the Python virtualenv live under `~/.dot-agent/state/tools/`.
- The browser template loads only local files.
- The Python renderer fails if Playwright attempts any HTTP(S) request.
- The tracked JS bundle is intentionally committed so a network-disabled agent
  session can render after runtime setup/browser install.
- Rebuild the bundle only when package pins or bundle source change:

```bash
~/.dot-agent/skills/excalidraw-diagram/scripts/build-renderer-bundle.sh
```

Smoke test:

```bash
~/.dot-agent/skills/excalidraw-diagram/scripts/test-offline-renderer.sh
```

Artifact rule:

- A human-facing PNG counts as Excalidraw output only when
  `render-excalidraw.sh` produced it from the matching `.excalidraw` file.
- Manual PNG fallbacks must be called out as fallback/non-rendered artifacts.
