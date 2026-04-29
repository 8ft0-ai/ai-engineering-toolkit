---
name: sprint-docs
description: Create or update <project_name> sprint plans, implementation reports, and backlog links using templates and consistent structure.
metadata:
  short-description: Draft and update sprint docs
---

# <project_name> Sprint Docs

Use this skill when creating or updating sprint plans and implementation reports in your repo’s sprint docs folder (default: `planning/`).

## Quick start (preferred)

1) Run the template script:
   - `python skills/sprint-docs/scripts/new_sprint_docs.py --sprint 04 --out planning --focus "Label refinement"`
2) Review and edit the generated files.
3) Ensure the `Related:` links are correct and point to the new sprint docs and `BACKLOG.md`.

## Manual workflow

- Copy templates from `assets/` into `projects/<project_name>/planning/`.
- Replace placeholders (e.g., `{{SPRINT_ID}}`, `{{SPRINT_TITLE}}`, `{{SPRINT_FOCUS}}`, `{{DATE}}`).
- Keep the stage/goal/exit-criteria structure consistent with previous sprints.
- Include a `Related:` line linking to the prior sprint plan/report and `BACKLOG.md`.

## Files

- `assets/sprint-plan-template.md`
- `assets/sprint-implementation-report-template.md`
- `scripts/new_sprint_docs.py`
