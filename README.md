# sprint-docs-marketplace

This repository is both:
- a **Claude Code plugin marketplace** (`.claude-plugin/marketplace.json`), and
- a packaged **plugin** (`./plugins/sprint-docs/`) that generates sprint documentation.

## Publish checklist

Before publishing, edit these fields:
- `.claude-plugin/marketplace.json` → `owner.name`
- `.claude-plugin/marketplace.json` → `name` (optional; becomes the marketplace name)
- `plugins/sprint-docs/.claude-plugin/plugin.json` → `version` (when releasing updates)

## Install (local)

From Claude Code:

1. Add marketplace:
   `/plugin marketplace add ./path/to/this-repo`

2. Install plugin:
   `/plugin install sprint-docs@sprint-docs-marketplace`

Restart Claude Code after installing.

## Install (GitHub)

1. Push this repo to GitHub.
2. In Claude Code:
   - `/plugin marketplace add owner/repo`
   - `/plugin install sprint-docs@sprint-docs-marketplace`

## Usage

- Slash command: `/new-sprint` (then follow the instructions it prints), or
- Deterministic generator:
  `python skills/sprint-docs/scripts/new_sprint_docs.py --sprint 04 --focus "Label refinement" --title "Data alignment" --out planning`
