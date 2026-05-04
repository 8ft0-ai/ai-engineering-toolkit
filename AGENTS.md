# Agent Notes

## Repo Shape
- This repo is not a conventional app/library workspace.
- Tracked deliverables live under `configs/`. The manifest `config-sync.json` defines which files/directories are synced to local home directories via `scripts/sync-configs.py`.
- The Claude Code plugin assets are under `configs/claude/`:
  - Slash command contract: `configs/claude/commands/new-sprint.md`
  - Skill definition and templates: `configs/claude/skills/sprint-docs/` (`SKILL.md`, `assets/`, `scripts/new_sprint_docs.py`)
- The former `tools/` directory (local mirrors) has been deleted; do not rely on it.

## Source Of Truth
- For config sync: `config-sync.json` is the manifest; actual tracked copies are under `configs/`.
- For sprint-docs content: `configs/claude/commands/new-sprint.md` and `configs/claude/skills/sprint-docs/SKILL.md` (plus templates in `configs/claude/skills/sprint-docs/assets/`) define behavior.
- The root `README.md` is partially stale: it refers to `.claude-plugin/...`, `plugins/sprint-docs/...`, and `skills/...` at the repo root. Use the actual paths under `configs/claude/` instead.
- If docs and manifests disagree, trust the tracked files under `configs/`.

## Local-Only Folders
- The `tools/` subdirectories (e.g., `tools/codex/`, `tools/litellm/`, `tools/opencode/`) were legacy local mirrors and are not tracked. They have been deprecated; the tracked copies now live under `configs/`.
- Live config locations (e.g., `~/.claude/`, `~/.codex/`, `~/.config/opencode/`) are outside the repo. Use `scripts/sync-configs.py` to manage them.

## Editing Guidance
- When modifying tracked config files, edit the file under `configs/` and run `python3 scripts/sync-configs.py push` to propagate changes.
- When adding or removing tracked entries, update `config-sync.json` accordingly.
- Do not add secrets, caches, `node_modules/`, or absolute-path symlinks.
- For sprint-docs content, keep `configs/claude/commands/new-sprint.md` aligned with `configs/claude/skills/sprint-docs/SKILL.md` and the templates in `configs/claude/skills/sprint-docs/assets/`; the command spec and templates duplicate structure on purpose.
- For publishing, create `.claude-plugin/marketplace.json` (set `owner.name`, optional `name`) and `plugins/sprint-docs/.claude-plugin/plugin.json` (set `version`). See `README.md` for required fields. These files are not currently tracked in the repo.
- The deterministic generator `configs/claude/skills/sprint-docs/scripts/new_sprint_docs.py` is broken (SyntaxError as of 2026-05-04); do not rely on it.

## Verification
- No repo-level build/test/lint setup.
- Check sync status: `python3 scripts/sync-configs.py status`.
- Test sync tooling with `python3 scripts/sync-configs.py pull` / `push` after changes.
- The slash command and skill files are plain text; manually verify formatting after edits.
