#!/usr/bin/env python3
from __future__ import annotations

import argparse
import keyword
import re
import sys
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "database-template"
DEPENDENCIES = ("alembic", "psycopg[binary]", "sqlmodel")
MUTABLE_TARGETS = {
    Path("src/package_name/db/__init__.py"),
    Path("src/package_name/db/models/__init__.py"),
}


def valid_package(value: str) -> str:
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", value) or keyword.iskeyword(value):
        raise argparse.ArgumentTypeError(f"Invalid Python package: {value!r}")
    return value


def detect_package(root: Path) -> str:
    src = root / "src"
    candidates = sorted(
        path.name
        for path in src.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    ) if src.is_dir() else []
    if len(candidates) != 1:
        raise ValueError(
            "Cannot detect one import package under src; pass --package explicitly"
        )
    return candidates[0]


def render(value: str, package_name: str) -> str:
    return value.replace("{{package_name}}", package_name)


def target_relative(source: Path, package_name: str) -> Path:
    relative = source.relative_to(TEMPLATE_ROOT)
    return Path(*(package_name if part == "package_name" else part for part in relative.parts))


def add_dependencies(content: str) -> str:
    missing = [item for item in DEPENDENCIES if f'"{item}"' not in content]
    if not missing:
        return content
    lines = content.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == "dependencies = ["), None)
    if start is None:
        raise ValueError("pyproject.toml has no multiline [project] dependencies array")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "]"), None)
    if end is None:
        raise ValueError("pyproject.toml dependencies array is not closed")
    lines[end:end] = [f'    "{item}",\n' for item in missing]
    return "".join(lines)


def add_env_example(content: str) -> str:
    block = (
        'DATABASE_URL="postgresql+psycopg://postgres:postgres@127.0.0.1:5432/app"\n'
        'DB_ECHO="false"\n'
    )
    if "DATABASE_URL=" in content:
        return content
    return content.rstrip() + "\n\n" + block


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add SQLModel, PostgreSQL, and Alembic to a src-layout project."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--package", type=valid_package)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.project_root.resolve()
    pyproject = root / "pyproject.toml"
    env_example = root / ".env.example"
    if not pyproject.is_file():
        print(f"error: missing {pyproject}", file=sys.stderr)
        return 2
    try:
        package_name = args.package or detect_package(root)
        pyproject_content = add_dependencies(pyproject.read_text(encoding="utf-8"))
        env_content = add_env_example(
            env_example.read_text(encoding="utf-8") if env_example.exists() else ""
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    planned: dict[Path, str] = {pyproject: pyproject_content, env_example: env_content}
    relative_by_target: dict[Path, Path] = {}
    for source in sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file()):
        target_rel = target_relative(source, package_name)
        target = root / target_rel
        planned[target] = render(source.read_text(encoding="utf-8"), package_name)
        relative_by_target[target] = source.relative_to(TEMPLATE_ROOT)

    conflicts: list[Path] = []
    for target, content in planned.items():
        if not target.exists():
            action = "CREATE"
        elif target.read_text(encoding="utf-8") == content:
            action = "UNCHANGED"
        elif relative_by_target.get(target) in MUTABLE_TARGETS:
            action = "PRESERVE"
            planned[target] = target.read_text(encoding="utf-8")
        elif target in (pyproject, env_example):
            action = "UPDATE"
        else:
            action = "CONFLICT"
            conflicts.append(target)
        print(f"{action} {target}")

    if conflicts:
        print("error: resolve conflicting files before generation", file=sys.stderr)
        return 2
    if args.dry_run:
        return 0
    for target, content in planned.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

