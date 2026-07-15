#!/usr/bin/env python3
from __future__ import annotations

import argparse
import keyword
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "resource-template"
SUPPORTED_TYPES = {
    "str": ("str", "str"),
    "int": ("int", "int"),
    "float": ("float", "float"),
    "bool": ("bool", "bool"),
    "datetime": ("datetime", "datetime"),
    "date": ("date", "date"),
    "UUID": ("UUID", "UUID"),
    "Decimal": ("Decimal", "Decimal"),
    "EmailStr": ("str", "EmailStr"),
}
RESERVED_FIELDS = {"id", "created_at", "updated_at"}


@dataclass(frozen=True)
class FieldSpec:
    name: str
    kind: str
    optional: bool = False
    unique: bool = False

    @property
    def model_type(self) -> str:
        return SUPPORTED_TYPES[self.kind][0]

    @property
    def schema_type(self) -> str:
        return SUPPORTED_TYPES[self.kind][1]


def snake_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()
    if (
        not normalized
        or not normalized.isidentifier()
        or keyword.iskeyword(normalized)
        or normalized in RESERVED_FIELDS
    ):
        raise argparse.ArgumentTypeError(f"Invalid or reserved name: {value!r}")
    return normalized


def parse_field(value: str) -> FieldSpec:
    parts = value.split(":")
    if len(parts) < 2:
        raise argparse.ArgumentTypeError("Use NAME:TYPE[:optional][:unique]")
    name = snake_name(parts[0])
    kind = parts[1]
    if kind not in SUPPORTED_TYPES:
        raise argparse.ArgumentTypeError(
            f"Unsupported type {kind!r}; choose {', '.join(SUPPORTED_TYPES)}"
        )
    modifiers = parts[2:]
    unknown = sorted(set(modifiers) - {"optional", "unique"})
    if unknown or len(modifiers) != len(set(modifiers)):
        raise argparse.ArgumentTypeError(f"Invalid field modifiers: {modifiers}")
    return FieldSpec(name, kind, "optional" in modifiers, "unique" in modifiers)


def class_name(resource: str) -> str:
    return "".join(part.capitalize() for part in resource.split("_"))


def pluralize(resource: str) -> str:
    if resource.endswith("y") and not resource.endswith(("ay", "ey", "iy", "oy", "uy")):
        return resource[:-1] + "ies"
    if resource.endswith(("s", "x", "z", "ch", "sh")):
        return resource + "es"
    return resource + "s"


def detect_package(root: Path) -> str:
    src = root / "src"
    candidates = sorted(
        path.name
        for path in src.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    ) if src.is_dir() else []
    if len(candidates) != 1:
        raise ValueError("Cannot detect one package under src; pass --package")
    return candidates[0]


def field_lines(fields: list[FieldSpec], mode: str) -> str:
    lines: list[str] = []
    for field in fields:
        if mode == "model":
            annotation = field.model_type + (" | None" if field.optional else "")
            args = []
            if field.optional:
                args.append("default=None")
            if field.unique:
                args.append("unique=True")
            suffix = f" = Field({', '.join(args)})" if args else ""
        elif mode == "create":
            annotation = field.schema_type + (" | None" if field.optional else "")
            suffix = " = None" if field.optional else ""
        elif mode == "update":
            annotation = field.schema_type + " | None"
            suffix = " = None"
        else:
            annotation = field.schema_type + (" | None" if field.optional else "")
            suffix = ""
        lines.append(f"    {field.name}: {annotation}{suffix}")
    return "\n".join(lines)


def sample_value(field: FieldSpec) -> str:
    values = {
        "str": f'"sample-{field.name}"',
        "EmailStr": '"sample@example.com"',
        "int": "7",
        "float": "1.5",
        "bool": "True",
        "datetime": '"2025-01-02T03:04:05Z"',
        "date": '"2025-01-02"',
        "UUID": '"12345678-1234-5678-1234-567812345678"',
        "Decimal": '"12.50"',
    }
    return values[field.kind]


def imports(fields: list[FieldSpec], schema: bool) -> str:
    needed = {field.schema_type if schema else field.model_type for field in fields}
    lines: list[str] = []
    date_types = sorted(needed & {"date", "datetime"})
    if date_types:
        lines.append(f"from datetime import {', '.join(date_types)}")
    if "Decimal" in needed:
        lines.append("from decimal import Decimal")
    if "UUID" in needed:
        lines.append("from uuid import UUID")
    if schema and "EmailStr" in needed:
        lines.append("from pydantic import EmailStr")
    return "\n".join(lines)


def render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"{{[^}]+}}", template)
    if unresolved:
        raise ValueError(f"Unresolved template values: {unresolved}")
    return template


def add_dependency(content: str, dependency: str) -> str:
    if f'"{dependency}"' in content:
        return content
    lines = content.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == "dependencies = ["), None)
    if start is None:
        raise ValueError("pyproject.toml has no multiline dependencies array")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "]"), None)
    if end is None:
        raise ValueError("pyproject.toml dependencies array is not closed")
    lines.insert(end, f'    "{dependency}",\n')
    return "".join(lines)


def append_registration(content: str, marker: str, block: str) -> str:
    if marker in content:
        return content
    return content.rstrip() + "\n\n" + block.rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate one layered FastAPI CRUD resource.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--package", type=snake_name)
    parser.add_argument("--resource", required=True, type=snake_name)
    parser.add_argument("--plural", type=snake_name)
    parser.add_argument("--field", action="append", required=True, type=parse_field)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.project_root.resolve()
    try:
        package = args.package or detect_package(root)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    fields: list[FieldSpec] = args.field
    if len({field.name for field in fields}) != len(fields):
        print("error: duplicate field names", file=sys.stderr)
        return 2
    package_root = root / "src" / package
    router_file = package_root / "api" / "router.py"
    model_registry = package_root / "db" / "models" / "__init__.py"
    engine_file = package_root / "db" / "engine.py"
    pyproject = root / "pyproject.toml"
    required = (router_file, model_registry, engine_file, pyproject)
    missing = [path for path in required if not path.is_file()]
    if missing:
        print("error: missing compatible project files: " + ", ".join(map(str, missing)), file=sys.stderr)
        return 2

    resource = args.resource
    plural = args.plural or pluralize(resource)
    cls = class_name(resource)
    values = {
        "package_name": package,
        "resource_name": resource,
        "plural_name": plural,
        "class_name": cls,
        "model_imports": imports(fields, schema=False),
        "schema_imports": imports(fields, schema=True),
        "model_fields": field_lines(fields, "model"),
        "create_fields": field_lines(fields, "create"),
        "update_fields": field_lines(fields, "update"),
        "read_fields": field_lines(fields, "read"),
        "sample_fields": "\n".join(
            f'        "{field.name}": {sample_value(field)},' for field in fields
        ),
        "unique_test": (
            "\n\ndef test_duplicate_unique_value_returns_conflict(client: TestClient) -> None:\n"
            "    payload = sample_payload()\n"
            f'    assert client.post("/{plural}", json=payload).status_code == 201\n'
            f'    response = client.post("/{plural}", json=payload)\n\n'
            "    assert response.status_code == 409\n"
        ) if any(field.unique for field in fields) else "",
    }

    targets: dict[Path, str] = {}
    mapping = {
        "model.py.tmpl": package_root / "db" / "models" / f"{resource}.py",
        "schemas.py.tmpl": package_root / "schemas" / f"{resource}.py",
        "repository.py.tmpl": package_root / "repositories" / f"{resource}.py",
        "service.py.tmpl": package_root / "services" / f"{resource}.py",
        "route.py.tmpl": package_root / "api" / "routes" / f"{resource}.py",
        "test.py.tmpl": root / "tests" / f"test_{resource}_api.py",
    }
    try:
        for template_name, target in mapping.items():
            targets[target] = render(
                (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8"), values
            )
        pyproject_content = pyproject.read_text(encoding="utf-8")
        if any(field.kind == "EmailStr" for field in fields):
            pyproject_content = add_dependency(pyproject_content, "email-validator")
        targets[pyproject] = pyproject_content
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    marker = f"# generated-resource: {resource}"
    targets[router_file] = append_registration(
        router_file.read_text(encoding="utf-8"),
        marker,
        f"{marker}\nfrom {package}.api.routes.{resource} import router as {resource}_router\n\nrouter.include_router({resource}_router)",
    )
    targets[model_registry] = append_registration(
        model_registry.read_text(encoding="utf-8"),
        marker,
        f"{marker}\nfrom {package}.db.models.{resource} import {cls} as {cls}",
    )

    for directory in ("api/routes", "schemas", "repositories", "services"):
        init = package_root / directory / "__init__.py"
        if not init.exists():
            targets[init] = '"""Generated package."""\n'

    conflicts: list[Path] = []
    for target, content in targets.items():
        if not target.exists():
            action = "CREATE"
        elif target.read_text(encoding="utf-8") == content:
            action = "UNCHANGED"
        elif target in (router_file, model_registry, pyproject):
            action = "UPDATE"
        else:
            action = "CONFLICT"
            conflicts.append(target)
        print(f"{action} {target}")
    if conflicts:
        print("error: resolve conflicting resource files before generation", file=sys.stderr)
        return 2
    if args.dry_run:
        return 0
    for target, content in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

