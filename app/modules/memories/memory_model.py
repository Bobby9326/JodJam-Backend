from datetime import date as Date, datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class Mood(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    TIRED = "tired"
    STRESSED = "stressed"
    EXCITED = "excited"
    ANGRY = "angry"
    BORED = "bored"
    LONELY = "lonely"


class Memory(SQLModel, table=True):
    __tablename__ = "memories"

    __table_args__ = (
        UniqueConstraint("user_id", "memory_date"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )

    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="CASCADE"
    )

    memory_date: Date = Field(
        nullable=False
    )

    image_path: str = Field(
        nullable=False
    )

    note: str = Field(
        nullable=False
    )

    mood: Mood = Field(
        default=None
    )

    rating: int = Field(
        default=None,
        ge=1,
        le=5
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )