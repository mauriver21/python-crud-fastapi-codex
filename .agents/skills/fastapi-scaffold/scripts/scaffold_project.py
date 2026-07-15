#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "project-template"


def normalize_project(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    if not normalized:
        raise argparse.ArgumentTypeError("Project name must contain a letter or digit")
    return normalized


def render(content: str, project_name: str) -> str:
    return content.replace("{{project_name}}", project_name)


def template_files() -> list[Path]:
    return sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a minimal Python 3.12 FastAPI project."
    )
    parser.add_argument("destination", type=Path)
    parser.add_argument("--project-name", required=True, type=normalize_project)
    parser.add_argument(
        "--existing-repository",
        action="store_true",
        help="Allow generation in an existing Git repository when no target files conflict",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print planned files without writing"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    destination = args.destination.resolve()

    files = template_files()
    if not files:
        print(f"error: template is empty: {TEMPLATE_ROOT}", file=sys.stderr)
        return 2

    if destination.exists() and not destination.is_dir():
        print(f"error: destination is not a directory: {destination}", file=sys.stderr)
        return 2

    destination_is_nonempty = destination.exists() and any(destination.iterdir())
    if destination_is_nonempty and not args.existing_repository:
        print(f"error: destination is not an empty directory: {destination}", file=sys.stderr)
        return 2

    if args.existing_repository and not (destination / ".git").exists():
        print(f"error: destination is not a Git repository: {destination}", file=sys.stderr)
        return 2

    planned_files = [
        (
            source,
            destination / source.relative_to(TEMPLATE_ROOT),
        )
        for source in files
    ]
    conflicts = [target for _, target in planned_files if target.exists()]
    if conflicts:
        for target in conflicts:
            print(f"error: target already exists: {target}", file=sys.stderr)
        return 2

    for _, target in planned_files:
        print(f"CREATE {target}")

    if args.dry_run:
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    for source, target in planned_files:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            render(source.read_text(), args.project_name),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
