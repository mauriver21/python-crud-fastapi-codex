---
name: fastapi-configure-sqlmodel-database
description: Add typed PostgreSQL configuration, SQLModel engine and session dependencies, and Alembic migrations to a Python 3.12 FastAPI project. Use when Codex needs to configure a database, add PostgreSQL or SQLModel, establish get_settings/get_engine/get_session interfaces, or introduce versioned migrations to a compatible src-layout service.
---

# FastAPI Configure SQLModel Database

Integrate database infrastructure without introducing domain models.

## Workflow

1. Inspect `pyproject.toml`, the import package, existing settings, and any database or migration files.
2. Prefer adapting existing conventions when the project is not compatible with the shared scaffold contract.
3. For a compatible project, preview the deterministic integration:

   ```bash
   python3.12 scripts/add_database.py --project-root <root> --dry-run
   ```

4. Resolve every reported conflict deliberately. Never overwrite a differing database or Alembic file.
5. Run without `--dry-run`, then create environment files from `.env.example`.
6. Read [references/database-workflow.md](references/database-workflow.md) before registering models or creating revisions.
7. Run imports, tests, and an Alembic upgrade against a disposable database.

## Guardrails

- Keep credentials in environment files that are ignored by version control.
- Inject `Session` through `get_session`; never create a global session.
- Let services control commits and rollbacks; let repositories issue queries.
- Import all table modules before Alembic reads `SQLModel.metadata`.
- Generate and review revisions; do not use `create_all()` as a production migration system.
