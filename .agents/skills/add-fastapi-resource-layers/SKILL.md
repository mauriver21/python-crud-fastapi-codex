---
name: add-fastapi-resource-layers
description: Generate a layered FastAPI CRUD resource with request/response schemas, SQLModel table, repository, service, routes, router registration, and API tests. Use when Codex needs to add an entity, REST resource, CRUD endpoints, pagination, or routes → services → repositories → database-model layers to a compatible FastAPI and SQLModel project.
---

# Add FastAPI Resource Layers

Generate one coherent vertical slice while preserving strict layer boundaries.

## Workflow

1. Inspect the package, database session dependency, router aggregator, model registry, and existing names.
2. Add database infrastructure first with `configure-sqlmodel-database` when `db/engine.py` is absent.
3. Define each field as `name:type`, optionally adding `optional`, `unique`, or both. Read [references/field-spec.md](references/field-spec.md).
4. Preview generation:

   ```bash
   python3.12 scripts/add_resource.py --project-root <root> --resource widget \
     --field name:str --field code:str:unique --dry-run
   ```

5. Resolve conflicts rather than overwriting them, then rerun without `--dry-run`.
6. Create and review an Alembic revision. Never create tables from application startup.
7. Run the generated tests and inspect OpenAPI request/response schemas.
8. Read [references/jwt-auth.md](references/jwt-auth.md) only when authentication is requested.

## Guardrails

- Keep HTTP conversion in routes, business rules and transactions in services, and queries in repositories.
- Return response schemas rather than table objects as the public contract.
- Inject sessions with `Depends(get_session)`.
- Preserve existing router and model registrations; add each generated registration once.
- Adapt manually for relationships, composite keys, domain-specific validation, filtering, or authorization.
