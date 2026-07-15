from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from utils.utc_now import utc_now


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    name: str = Field(max_length=256)
    email: str = Field(max_length=256)
    password: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = Field(default=None)
