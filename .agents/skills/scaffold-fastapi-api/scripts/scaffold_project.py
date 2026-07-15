#!/usr/bin/env python3
from __future__ import annotations

import argparse
import keyword
import re
import sys
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "project-template"


def normalize_package(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()
    if not normalized or normalized[0].isdigit() or keyword.iskeyword(normalized):
        raise argparse.ArgumentTypeError(f"Cannot derive a Python package from {value!r}")
    return normalized


def normalize_project(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    if not normalized:
        raise argparse.ArgumentTypeError("Project name must contain a letter or digit")
    return normalized


def destination_path(relative: Path, package_name: str) -> Path:
    parts = [package_name if part == "package_name" else part for part in relative.parts]
    return Path(*parts)


def render(content: str, project_name: str, package_name: str) -> str:
    return content.replace("{{project_name}}", project_name).replace(
        "{{package_name}}", package_name
    )


def template_files() -> list[Path]:
    return sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a minimal Python 3.12 FastAPI project."
    )
    parser.add_argument("destination", type=Path)
    parser.add_argument("--project-name", required=True, type=normalize_project)
    parser.add_argument("--package", type=normalize_package)
    parser.add_argument(
        "--dry-run", action="store_true", help="Print planned files without writing"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    destination = args.destination.resolve()
    package_name = args.package or normalize_package(args.project_name)

    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        print(f"error: destination is not an empty directory: {destination}", file=sys.stderr)
        return 2

    files = template_files()
    if not files:
        print(f"error: template is empty: {TEMPLATE_ROOT}", file=sys.stderr)
        return 2

    for source in files:
        relative = destination_path(source.relative_to(TEMPLATE_ROOT), package_name)
        print(f"CREATE {destination / relative}")

    if args.dry_run:
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    for source in files:
        relative = destination_path(source.relative_to(TEMPLATE_ROOT), package_name)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            render(source.read_text(), args.project_name, package_name),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

