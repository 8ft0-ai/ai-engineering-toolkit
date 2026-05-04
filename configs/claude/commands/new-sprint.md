---
description: Create sprint plan + implementation report in ./planning (or a specified folder).
argument-hint: <sprint-id> <focus> <title> [prev-id] [out-dir]
---

Create (or ensure) the output directory exists (default `planning/`), then write:

- `SPRINT-<sprint-id>-PLAN.md`
- `SPRINT-<sprint-id>-IMPLEMENTATION-REPORT.md`

Use the templates below and replace:
- `{{SPRINT_ID}}`, `{{PREV_SPRINT_ID}}`, `{{SPRINT_TITLE}}`, `{{SPRINT_FOCUS}}`, `{{DATE}}`

If an existing file would be overwritten, abort and ask the user for an explicit new sprint id or output folder.

## Plan template

```markdown
# Sprint {{SPRINT_ID}} Plan ({{SPRINT_TITLE}})

Related: [Sprint {{PREV_SPRINT_ID}} Plan](SPRINT-{{PREV_SPRINT_ID}}-PLAN.md), [Sprint {{PREV_SPRINT_ID}} Implementation Report](SPRINT-{{PREV_SPRINT_ID}}-IMPLEMENTATION-REPORT.md), [Backlog](BACKLOG.md)

Date: {{DATE}}

This plan focuses on {{SPRINT_FOCUS}}.

## Stage 0 - Scope and setup

Goal: Clarify what is in/out of scope and confirm baseline assumptions.

- [ ] Define scope boundaries and data constraints.
- [ ] Confirm baseline dataset and metrics inputs.

Exit criteria:
- Scope and inputs are documented and signed off.

## Stage 1 - Primary workstream

Goal: Execute the highest-impact work for this sprint.

- [ ] Task placeholder 1.
- [ ] Task placeholder 2.

Exit criteria:
- Primary workstream tasks are complete and measured.

## Stage 2 - Validation and reporting

Goal: Validate results and document outcomes.

- [ ] Summarize results and deltas.
- [ ] Capture risks, gaps, and next steps.

Exit criteria:
- Results are documented and ready for handoff.
```

## Implementation report template

```markdown
# Sprint {{SPRINT_ID}} Implementation Report

Related: [Sprint {{SPRINT_ID}} Plan](SPRINT-{{SPRINT_ID}}-PLAN.md), [Sprint {{PREV_SPRINT_ID}} Implementation Report](SPRINT-{{PREV_SPRINT_ID}}-IMPLEMENTATION-REPORT.md), [Backlog](BACKLOG.md)

Date: {{DATE}}

This report summarizes the implementation and outcomes of Sprint {{SPRINT_ID}}.

## Scope and objectives

- Objective 1.
- Objective 2.

## Summary of outcomes

- Key result 1.
- Key result 2.

## Stage 0 - Scope and setup

**Purpose**
- Summarize scope and baseline assumptions.

**Steps implemented**
- Step 1.

**Results and meaning**
- Result summary.

## Stage 1 - Primary workstream

**Purpose**
- What the stage targeted.

**Steps implemented**
- Step 1.

**Results and meaning**
- Result summary.

## Stage 2 - Validation and reporting

**Purpose**
- Validation and documentation.

**Steps implemented**
- Step 1.

**Results and meaning**
- Result summary.

## Risks and gaps

- Risk 1.
- Gap 1.

## Recommendations

1) Recommendation 1.
2) Recommendation 2.
```

Tip: If you prefer a deterministic generator, run:
`python skills/sprint-docs/scripts/new_sprint_docs.py --sprint <id> --focus "<focus>" --title "<title>" --out <out-dir>`
