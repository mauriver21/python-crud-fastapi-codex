# Python CRUD REST API

FastAPI REST API for user management with PostgreSQL, SQLModel, JWT
authentication, password hashing, database migrations, and integration tests.

## Requirements

- Python `3.12.6`
- PostgreSQL
- `pip`

## Project Structure

```text
.
├── .env.example
├── conftest.py
├── pyproject.toml
├── src
│   ├── config.py
│   ├── controllers
│   │   ├── user.py
│   │   └── user_test.py
│   ├── db
│   │   ├── engine.py
│   │   ├── migrate.py
│   │   ├── migrations
│   │   └── schema
│   ├── interfaces
│   ├── middlewares
│   ├── models
│   ├── repositories
│   ├── main.py
│   └── routes.py
└── tests
    ├── constants.py
    └── utils.py
```

## Setup

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode with its testing dependencies:

```bash
pip install -e ".[test]"
```

Runtime dependencies, test extras, package discovery, and command-line entry
points are defined in `pyproject.toml`.

Create the development environment file:

```bash
cp .env.example .env.dev
```

Update `.env.dev` with the PostgreSQL database credentials and a secure JWT
secret, then create the configured database.

## Configuration

The application reads `APP_ENV` and loads the corresponding file from the
project root:

- `development` loads `.env.dev` and is the default.
- `test` loads `.env.test`.
- `production` loads `.env.prod`.

Available variables:

```env
ALLOWED_ORIGINS="http://localhost:3000"
PORT="3000"
JWT_SECRET_KEY="change-me"
JWT_EXPIRES_IN_HOURS=8
DISK_STORAGE_PATH="./storage"
DB_DIALECT="postgresql"
DB_HOST="127.0.0.1"
DB_PORT="5434"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_NAME="ecommerce"
```

Configuration is available in Python through:

```python
from config import config
```

## Database Migrations

Apply all migrations to the development database:

```bash
APP_ENV=development ./.venv/bin/db-migrate upgrade
```

Other migration commands:

```bash
./.venv/bin/db-migrate list
APP_ENV=development ./.venv/bin/db-migrate downgrade
APP_ENV=development ./.venv/bin/db-migrate upgrade --name create_users_table
```

## Run The API

Start the development server from the project root:

```bash
./.venv/bin/fastapi dev src/main.py
```

Alternatively, use Uvicorn:

```bash
./.venv/bin/python -m uvicorn main:app --reload
```

FastAPI exposes interactive API documentation at
`http://127.0.0.1:8000/docs`.

## Dependencies

| Dependency | Purpose |
| --- | --- |
| `fastapi` | Defines the REST API, routes, request validation, dependency injection, and exception handling. |
| `sqlmodel` | Defines database models and provides SQLAlchemy-based sessions and queries. |
| `psycopg` | Connects SQLModel and SQLAlchemy to PostgreSQL. |
| `pwdlib[argon2]` | Hashes and verifies user passwords using Argon2. |
| `PyJWT` | Creates and validates JWT access tokens. |
| `python-dotenv` | Loads environment-specific configuration from `.env` files. |
| `uvicorn` | Runs the FastAPI application as an ASGI server. |
| `pytest` | Runs the integration test suite and its session fixtures. |
| `setuptools` | Builds the project, supports editable installation, and creates the `db-migrate` command. |

## Testing

The tests are integration tests that exercise the FastAPI routes, JWT
middleware, repositories, models, and a dedicated PostgreSQL test database.

Create and configure the test environment file. It must point to a separate
database because test cleanup deletes user records.

```bash
cp .env.example .env.test
```

Create the configured test database and apply its migrations:

```bash
APP_ENV=test ./.venv/bin/db-migrate upgrade
```

Run the complete test suite:

```bash
./.venv/bin/pytest
```

Run only the user controller tests:

```bash
./.venv/bin/pytest src/controllers/user_test.py
```

The editable installation makes the `src` modules importable without modifying
`PYTHONPATH`. Pytest configuration lives in `pyproject.toml`. The root
`conftest.py` sets `APP_ENV=test` and initializes the exclusive test user once
per test session. Test cleanup deletes every other user while preserving that
account.
