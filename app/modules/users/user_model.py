from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        primary_key=True
    )

    email: EmailStr = Field(
        unique=True,
        index=True,
        nullable=False
    )

    username: str = Field(
        unique=True,
        nullable=False
    )

    profile_url: str | None = Field(
        default=None
    )

    bio: str | None = Field(
        default=None
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )