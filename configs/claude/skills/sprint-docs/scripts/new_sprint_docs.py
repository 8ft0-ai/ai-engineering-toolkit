#!/usr/bin/env python3
import argparse
import datetime as dt
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Could not find repo root (.git). Run this command from inside a git repo (your project).")


def normalize_sprint_id(raw: str) -> str:
    raw = raw.strip()
    if raw.isdigit():
        return raw.zfill(2)
    return raw


def previous_sprint_id(sprint_id: str) -> str:
    if sprint_id.isdigit():
        value = int(sprint_id)
        if value > 1:
            return str(value - 1).zfill(2)
    return "{{PREV_SPRINT_ID}}"


def render_template(template_path: Path, replacements: dict) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Create sprint plan + implementation report from templates.")
    parser.add_argument("--sprint", required=True, help="Sprint number or ID, e.g., 03")
    parser.add_argument("--focus", default="TBD", help="Short focus line for the sprint")
    parser.add_argument("--title", default="TBD", help="Sprint title")
    parser.add_argument("--prev", default=None, help="Previous sprint ID, e.g., 02")
    parser.add_argument("--out", default="planning", help="Output directory relative to repo root (default: planning)")
    args = parser.parse_args()

    sprint_id = normalize_sprint_id(args.sprint)
    prev_id = normalize_sprint_id(args.prev) if args.prev else previous_sprint_id(sprint_id)

    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    templates_dir = skill_dir / "assets"

    repo_root = find_repo_root(Path.cwd())
    planning_dir = repo_root / args.outplan_path = planning_dir / f"SPRINT-{sprint_id}-PLAN.md"
    report_path = planning_dir / f"SPRINT-{sprint_id}-IMPLEMENTATION-REPORT.md"

    if plan_path.exists() or report_path.exists():
        raise SystemExit("Sprint files already exist; aborting to avoid overwrite.")

    replacements = {
        "SPRINT_ID": sprint_id,
        "PREV_SPRINT_ID": prev_id,
        "SPRINT_TITLE": args.title,
        "SPRINT_FOCUS": args.focus,
        "DATE": dt.date.today().isoformat(),
    }

    plan_template = templates_dir / "sprint-plan-template.md"
    report_template = templates_dir / "sprint-implementation-report-template.md"

    plan_content = render_template(plan_template, replacements)
    report_content = render_template(report_template, replacements)

    planning_dir.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan_content, encoding="utf-8")
    report_path.write_text(report_content, encoding="utf-8")

    print(f"Created: {plan_path}")
    print(f"Created: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
