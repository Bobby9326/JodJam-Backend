from sqlalchemy import extract
from sqlmodel import Session, select
from app.modules.memories.memory_model import Memory


class StatRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_year(self, user_id: str, year: int) -> list[Memory]:
        statement = select(Memory).where(
            Memory.user_id == user_id,
            extract('year', Memory.memory_date) == year,
        )
        return self.db.exec(statement).all()