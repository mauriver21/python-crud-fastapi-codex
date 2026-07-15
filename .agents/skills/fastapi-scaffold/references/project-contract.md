# Reference project contract

The scaffold reproduces this complete layout from `python-crud-rest-api`:

```text
.
├── .env.example
├── .gitignore
├── .python-version
├── .vscode/settings.json
├── README.md
├── conftest.py
├── pyproject.toml
├── src/
│   ├── config.py
│   ├── controllers/
│   │   ├── user.py
│   │   └── user_test.py
│   ├── db/
│   │   ├── engine.py
│   │   ├── migrate.py
│   │   ├── migrations/create_users_table.py
│   │   └── schema/users.py
│   ├── interfaces/
│   │   ├── Config.py
│   │   ├── DbConfig.py
│   │   └── User*.py
│   ├── middlewares/auth.py
│   ├── models/user.py
│   ├── repositories/user.py
│   ├── utils/utc_now.py
│   ├── main.py
│   └── routes.py
└── tests/
    ├── constants.py
    └── utils.py
```

Use the flat `src` root and absolute imports such as `from main import app`, `import controllers.user`, and `from db.engine import engine`. Keep directories as implicit namespace packages without `__init__.py` files.

Preserve the request flow `routes.py → controllers/ → repositories/ → models/ and db/schema/`. Preserve JWT middleware, SQLModel persistence, dotenv environment selection, the custom `db-migrate` command, and controller integration tests. Do not translate these conventions into a different architecture unless the user explicitly asks for a migration.
