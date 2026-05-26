from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: str = Field(
        default_factory=uuid4,
        primary_key=True
    )

    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )

    token: str = Field(
        unique=True,
        nullable=False,
        index=True
    )

    expires_at: datetime = Field(
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
