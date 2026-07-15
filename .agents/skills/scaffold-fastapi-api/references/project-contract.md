# Shared project contract

The three skills share this default layout:

```text
src/<package>/
├── api/
│   └── router.py
├── config.py
└── main.py
```

Database support adds `db/` and Alembic migrations. Resource generation adds:

```text
api/routes/ → services/ → repositories/ → db/models/
             schemas/ defines API request and response boundaries
```

Use dependency injection for sessions and other infrastructure. Routes translate HTTP input and output. Services own business rules and transaction decisions. Repositories own queries. SQLModel table classes describe persistence. Pydantic/SQLModel schemas prevent persistence-only fields from leaking into responses.

The project generator deliberately creates no database, authentication, CORS, or domain resource. Add only the capabilities requested by the user.

