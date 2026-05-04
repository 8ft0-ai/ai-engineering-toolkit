#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "config-sync.json"
STATE_PATH = REPO_ROOT / ".config-sync-state.json"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_repo_path(entry: dict) -> Path:
    return REPO_ROOT / entry["repo_path"]


def resolve_target_path(entry: dict) -> Path:
    return Path(entry["target_path"]).expanduser()


def existing_path(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"file:{digest.hexdigest()}"


def hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        rel = child.relative_to(path).as_posix().encode("utf-8")
        digest.update(rel)
        if child.is_symlink():
            digest.update(b"symlink")
            digest.update(str(child.readlink()).encode("utf-8"))
        elif child.is_file():
            digest.update(b"file")
            digest.update(child.read_bytes())
        elif child.is_dir():
            digest.update(b"dir")
    return f"dir:{digest.hexdigest()}"


def hash_path(path: Path, kind: str):
    if not existing_path(path):
        return None
    if kind == "file":
        if path.is_dir():
            raise ValueError(f"Expected file at {path}, found directory")
        return hash_file(path)
    if kind == "directory":
        if not path.is_dir():
            raise ValueError(f"Expected directory at {path}, found file")
        return hash_directory(path)
    raise ValueError(f"Unsupported kind: {kind}")


def copy_path(src: Path, dst: Path, kind: str) -> None:
    if kind == "file":
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return

    if kind == "directory":
        dst.parent.mkdir(parents=True, exist_ok=True)
        if existing_path(dst):
            if dst.is_dir() and not dst.is_symlink():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.copytree(src, dst)
        return

    raise ValueError(f"Unsupported kind: {kind}")


def classify(entry: dict, state_entry: dict) -> tuple[str, str | None, str | None]:
    kind = entry["kind"]
    repo_hash = hash_path(resolve_repo_path(entry), kind)
    target_hash = hash_path(resolve_target_path(entry), kind)

    if repo_hash == target_hash:
        return "in_sync", repo_hash, target_hash

    if not state_entry:
        return "different", repo_hash, target_hash

    repo_changed = repo_hash != state_entry.get("repo_hash")
    target_changed = target_hash != state_entry.get("target_hash")

    if repo_changed and target_changed:
        return "diverged", repo_hash, target_hash
    if repo_changed:
        return "repo_changed", repo_hash, target_hash
    if target_changed:
        return "target_changed", repo_hash, target_hash
    return "different", repo_hash, target_hash


def update_state_record(state: dict, entry_name: str, repo_hash, target_hash) -> None:
    state[entry_name] = {
        "repo_hash": repo_hash,
        "target_hash": target_hash,
    }


def print_status(manifest: dict, state: dict) -> int:
    exit_code = 0
    labels = {
        "in_sync": "in sync",
        "different": "different (no baseline)",
        "repo_changed": "repo changed",
        "target_changed": "target changed",
        "diverged": "diverged",
    }

    for entry in manifest["entries"]:
        status, repo_hash, target_hash = classify(entry, state.get(entry["name"]))
        print(f"{entry['name']}: {labels[status]}")
        print(f"  repo:   {entry['repo_path']}")
        print(f"  target: {entry['target_path']}")
        if repo_hash is None:
            print("  repo state: missing")
        if target_hash is None:
            print("  target state: missing")
        if status in {"different", "diverged"}:
            exit_code = 1
    return exit_code


def sync(manifest: dict, state: dict, direction: str, force: bool) -> int:
    exit_code = 0
    source_key = "repo" if direction == "push" else "target"
    destination_key = "target" if direction == "push" else "repo"

    for entry in manifest["entries"]:
        name = entry["name"]
        kind = entry["kind"]
        status, repo_hash, target_hash = classify(entry, state.get(name))
        repo_path = resolve_repo_path(entry)
        target_path = resolve_target_path(entry)
        src = repo_path if source_key == "repo" else target_path
        dst = target_path if destination_key == "target" else repo_path
        src_hash = repo_hash if source_key == "repo" else target_hash

        if status == "diverged" and not force:
            print(f"{name}: skipped (diverged; rerun with --force to overwrite destination)")
            exit_code = 1
            continue

        if src_hash is None:
            print(f"{name}: skipped ({source_key} source missing)")
            continue

        if repo_hash == target_hash:
            print(f"{name}: unchanged")
        else:
            copy_path(src, dst, kind)
            print(f"{name}: copied {source_key} -> {destination_key}")

        refreshed_repo_hash = hash_path(repo_path, kind)
        refreshed_target_hash = hash_path(target_path, kind)
        update_state_record(state, name, refreshed_repo_hash, refreshed_target_hash)

    save_json(STATE_PATH, state)
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync selected local config files with the repo-managed copies.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show differences between repo and live config paths")

    pull = subparsers.add_parser("pull", help="Copy live config changes into the repo")
    pull.add_argument("--force", action="store_true", help="Overwrite repo copy even if both sides changed")

    push = subparsers.add_parser("push", help="Copy repo config changes to live config paths")
    push.add_argument("--force", action="store_true", help="Overwrite live copy even if both sides changed")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    manifest = load_json(MANIFEST_PATH, default={"entries": []})
    state = load_json(STATE_PATH, default={})

    if args.command == "status":
        return print_status(manifest, state)
    if args.command == "pull":
        return sync(manifest, state, direction="pull", force=args.force)
    if args.command == "push":
        return sync(manifest, state, direction="push", force=args.force)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
