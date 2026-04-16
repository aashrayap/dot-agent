---
name: init-epic
description: "Bootstrap a cross-repo coordination workspace using the toolkit-rigby pattern: root AGENTS.md, README.md, gitignored sibling repos, inventory docs, and optional repo cloning. Use this before projects/focus when the user first needs a multi-repo coordination workspace."
argument-hint: <workspace description and repo map>
disable-model-invocation: true
---

# Init Epic

Use this when the user wants to stand up a coordination repo for a multi-repo initiative.

This skill captures the reusable pattern from `toolkit-rigby`: root coordination files, gitignored sibling repos, inventory stubs for each imported repo, and clear routing between current implementation repos, legacy reference repos, and the coordination repo itself.

## Workflow Position

- `init-epic` bootstraps the coordination repo.
- `projects` takes over once durable milestones and execution slices need tracking.
- `focus` chooses the active tracked project or slice for today.
- `morning-sync` reviews that state at day start.

## Context

Run `~/.dot-agent/skills/init-epic/scripts/init-epic-setup.sh --help` first so you know the scaffold contract.

Then inspect the current workspace:

- list the repo root
- read any existing `AGENTS.md`, `README.md`, `.gitignore`, and `docs/`
- determine whether the repo is empty, lightly scaffolded, or already in use

## Workflow

1. Parse the user's intended workspace:
   - workspace title
   - focus label
   - repo roster
   - which repos are `current` vs `legacy`
   - repo order for current implementation work
   - whether the user wants missing repos cloned locally
2. Translate each imported repo into a script entry:
   - `name`
   - `url`
   - `kind` (`current` or `legacy`)
   - short ownership/role sentence
3. Run the scaffold script from the target repo root. Minimum flags:

   ```bash
   ~/.dot-agent/skills/init-epic/scripts/init-epic-setup.sh \
     --workspace-title "Toolkit Rigby" \
     --focus "Rigby" \
     --repo "Toolkit.Web|https://example.com/Toolkit.Web|current|Current Rigby web app and host-side UI behavior." \
     --repo "Toolkit.API|https://example.com/Toolkit.API|current|Current Rigby backend and runtime support services." \
     --repo "workover-assistant|https://github.com/org/workover-assistant.git|legacy|Legacy Rigby reference implementation." \
     --init-git
   ```

4. Review the generated files and tighten any wording that should preserve the user's exact language.
5. If the user wants a fully bootstrapped local workspace, verify the remotes are reachable and rerun with `--clone-missing`.
6. If the work will be long-lived, hand off to `projects <slug>` after bootstrap. `init-epic` owns the workspace scaffold; `projects` owns milestone and execution-slice tracking. After that, use `focus` for day-level control and `morning-sync` for daily review.

## Outputs

The script scaffolds:

- `.gitignore` with a managed block for nested sibling repos
- `AGENTS.md`
- `README.md`
- `docs/inventory/*.md`
- optional `git init -b main`
- optional cloning of missing sibling repos into the repo root

## Rules

- Preserve existing user edits. Do not pass `--force` unless the user explicitly wants to replace the current scaffold or the files are still throwaway bootstrap output.
- Read existing root files before rerunning the scaffold. Do not overwrite a real workspace blindly.
- Keep this repo coordination-only. Production code belongs in the owning upstream repo.
- Use explicit `current` and `legacy` labels. Do not treat a legacy repo as current ownership by default.
- Keep repo-role sentences concise and specific. They feed directly into `AGENTS.md`, `README.md`, and inventory stubs.
- The order of `--repo` flags controls the current-repo implementation order written into `AGENTS.md`.
- After scaffolding, verify that nested repo directories are gitignored and that the generated docs match the intended repo split.

## When To Skip This Skill

Do not use `init-epic` for:

- a normal application repo with no nested sibling repos
- ongoing milestone management without workspace bootstrap needs
- feature planning inside an already-established coordination repo
