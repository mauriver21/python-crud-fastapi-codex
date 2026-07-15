---
name: scaffold-fastapi-api
description: Scaffold a new Python 3.12 FastAPI REST API with a src layout, typed application settings, health endpoint, packaging, and tests. Use when Codex needs to create a new FastAPI service, bootstrap a REST API repository, or establish the baseline project structure expected by the configure-sqlmodel-database and add-fastapi-resource-layers skills.
---

# Scaffold FastAPI API

Create the smallest runnable service before adding database or domain concerns.

## Workflow

1. Inspect the requested destination. Never replace an existing non-empty directory.
2. Choose a hyphenated project name and a valid snake_case import package.
3. Preview generation:

   ```bash
   python3.12 scripts/scaffold_project.py <destination> --project-name <name> --dry-run
   ```

4. Run the same command without `--dry-run` after reviewing the paths.
5. Read [references/project-contract.md](references/project-contract.md) before changing the generated layout or coordinating with the database/resource skills.
6. Create a virtual environment, install `-e ".[test]"`, and run `pytest`.

## Guardrails

- Preserve the `src/<package>` layout and absolute package imports.
- Keep `main.py` limited to application construction and router inclusion.
- Add transport endpoints below `api/`; do not place persistence or business logic in routes.
- Treat `.env.example` as documentation only. Never copy real credentials into generated output.
- Adapt the generated project after creation when the user has additional conventions; do not complicate the baseline generator with business-specific options.
