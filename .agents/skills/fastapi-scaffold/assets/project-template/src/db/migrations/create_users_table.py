from sqlmodel import SQLModel

from db.engine import engine
from db.schema.users import User


def upgrade() -> None:
    # Register the table metadata before creating the single target table.
    SQLModel.metadata.create_all(
        engine,
        tables=[User.__table__],
    )


def downgrade() -> None:
    User.__table__.drop(engine, checkfirst=True)


if __name__ == "__main__":
    upgrade()
