from __future__ import annotations

import argparse
import importlib
from pathlib import Path


MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
MIGRATIONS_PACKAGE = "db.migrations"


def get_migration_names() -> list[str]:
    return sorted(
        path.stem
        for path in MIGRATIONS_DIR.glob("*.py")
        if path.name != "__init__.py"
    )


def load_migration(name: str):
    return importlib.import_module(f"{MIGRATIONS_PACKAGE}.{name}")


def run_upgrades(target: str | None = None) -> None:
    names = [target] if target else get_migration_names()

    for name in names:
        migration = load_migration(name)
        if not hasattr(migration, "upgrade"):
            raise AttributeError(f"Migration '{name}' does not define upgrade()")
        print(f"Upgrading {name}")
        migration.upgrade()


def run_downgrades(target: str | None = None) -> None:
    names = [target] if target else list(reversed(get_migration_names()))

    for name in names:
        migration = load_migration(name)
        if not hasattr(migration, "downgrade"):
            raise AttributeError(f"Migration '{name}' does not define downgrade()")
        print(f"Downgrading {name}")
        migration.downgrade()


def list_migrations() -> None:
    for name in get_migration_names():
        print(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SQLModel migration modules.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available migrations")
    list_parser.set_defaults(func=lambda _: list_migrations())

    upgrade_parser = subparsers.add_parser("upgrade", help="Run upgrades")
    upgrade_parser.add_argument(
        "--name",
        help="Run only one migration by module name",
    )
    upgrade_parser.set_defaults(func=lambda args: run_upgrades(args.name))

    downgrade_parser = subparsers.add_parser("downgrade", help="Run downgrades")
    downgrade_parser.add_argument(
        "--name",
        help="Run only one migration by module name",
    )
    downgrade_parser.set_defaults(func=lambda args: run_downgrades(args.name))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    available = get_migration_names()

    if getattr(args, "name", None) and args.name not in available:
        parser.error(
            f"Unknown migration '{args.name}'. Available: {', '.join(available) or 'none'}"
        )

    args.func(args)


if __name__ == "__main__":
    main()
