# Managed Configs

This repo stores the canonical, committable copies of selected local config files under `configs/`.

Use `python3 scripts/sync-configs.py status` to see differences.
Use `python3 scripts/sync-configs.py pull` to copy live machine changes into the repo.
Use `python3 scripts/sync-configs.py push` to copy repo changes back to live locations.

The manifest lives in `config-sync.json`.

Deliberately excluded from version control:
- secrets and auth files such as `~/.codex/auth.json`
- caches and generated state such as `models_cache.json`, `node_modules/`, and lockfiles under live config folders
- absolute-path symlink mirrors under `tools/`
