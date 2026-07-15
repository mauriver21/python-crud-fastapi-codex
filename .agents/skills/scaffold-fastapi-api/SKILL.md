---
name: scaffold-fastapi-api
description: Scaffold a Python 3.12 FastAPI user CRUD API that reproduces the architecture and behavior of the python-crud-rest-api reference repository, including PostgreSQL, SQLModel, JWT authentication, custom migrations, dotenv configuration, controller tests, and flat src imports. Use when Codex needs to create or reproduce this complete reference application without modernizing its conventions.
---

# Scaffold FastAPI API

Reproduce the complete reference application from the bundled project template. Preserve its architecture and behavior instead of replacing its conventions with newer patterns.

## Workflow

1. Ask the user for the project destination path when they have not provided one. Wait for their answer; never infer the path from the current directory, repository name, or a default subdirectory.
2. Resolve and inspect the user-provided destination. Use an empty directory by default. When the user explicitly requests the root of an existing Git repository, preserve its `.git` directory and require that none of the generated target files already exist.
3. Choose a hyphenated project name. Change only the templated distribution name; preserve the reference module and file names.
4. Preview generation:

   ```bash
   python3.12 scripts/scaffold_project.py <destination> --project-name <name> --dry-run
   ```

   Add `--existing-repository` only when the user explicitly requests generation in an existing Git repository. The generator must verify `.git` and reject target-file conflicts.

5. Run the same command without `--dry-run` after reviewing the paths.
6. Read [references/project-contract.md](references/project-contract.md) before changing any generated file or directory.
7. Create a Python 3.12 virtual environment and install `-e ".[test]"`.
8. Create `.env.dev` and `.env.test` from `.env.example`, supply safe local PostgreSQL credentials and JWT secrets, create separate development and test databases, and run `db-migrate upgrade` for each environment.
9. Run `pytest` only against the dedicated test database. The suite deletes non-fixture user records.

## Guardrails

- Do not inspect, preview, or generate a project until the user has explicitly supplied its destination path.
- Never initialize a nested Git repository. Reuse an existing repository only when the user explicitly requests it.
- Never overwrite an existing target file, including in existing-repository mode.
- Preserve the reference's flat `src/` imports, directory names, PascalCase interface files, camelCase variables, controller-to-repository flow, global engine/session behavior, custom migration runner, and co-located `*_test.py` tests.
- Do not add `__init__.py` files or introduce an application-name package.
- Do not replace `routes.py` with router packages, dotenv with settings classes, custom migrations with Alembic, interfaces with renamed schemas, or the existing layers with a service layer unless the user separately requests that migration.
- Treat `.env.example` as documentation. Never bundle or copy real `.env.dev`, `.env.test`, or `.env.prod` credentials from a reference repository.
- Preserve the bundled reference behavior first; make user-requested deviations only after generation.
