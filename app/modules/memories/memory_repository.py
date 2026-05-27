from datetime import date as Date, timedelta
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.modules.memories.memory_model import Memory, Mood


class MemoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_date(self, user_id: str, memory_date: Date) -> Memory | None:
        statement = select(Memory).where(
            Memory.user_id == user_id,
            Memory.memory_date == memory_date,
        )
        return self.db.exec(statement).first()

    def get_by_year(self, user_id: str, year: int) -> list[Memory]:
        """Return all memories for a user in a given year."""
        start = Date(year, 1, 1)
        end = Date(year, 12, 31)
        statement = select(Memory).where(
            Memory.user_id == user_id,
            Memory.memory_date >= start,
            Memory.memory_date <= end,
        )
        return list(self.db.exec(statement).all())

    def get_range(self, user_id: str, start: Date, end: Date) -> list[Memory]:
        """Return memories between start and end dates (inclusive)."""
        statement = select(Memory).where(
            Memory.user_id == user_id,
            Memory.memory_date >= start,
            Memory.memory_date <= end,
        )
        return list(self.db.exec(statement).all())

    def create_memory(
        self,
        user_id: str,
        memory_date: Date,
        image_path: str,
        note: str,
        mood: Mood,
        rating: int,
    ) -> Memory:
        memory = Memory(
            user_id=user_id,
            memory_date=memory_date,
            image_path=image_path,
            note=note,
            mood=mood,
            rating=rating,
        )
        self.db.add(memory)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("A memory entry already exists for this date")
        self.db.refresh(memory)
        return memory