from datetime import date as Date
from typing import Optional

from pydantic import BaseModel, Field

from app.modules.memories.memory_model import Mood


# --- Request ---

class CreateMemoryRequest(BaseModel):
    note: str
    mood: Mood
    rating: int = Field(ge=1, le=5)
    memory_date: Date


# --- Shared ---

class DayEntry(BaseModel):
    date: Date
    has_entry: bool
    img_url: str | None = None


# --- Response ---

class CreateMemoryResponse(BaseModel):
    id: str
    memory_date: Date
    image_path: str
    note: str
    mood: Mood
    rating: int


class CalendarResponse(BaseModel):
    january: list[DayEntry]
    february: list[DayEntry]
    march: list[DayEntry]
    april: list[DayEntry]
    may: list[DayEntry]
    june: list[DayEntry]
    july: list[DayEntry]
    august: list[DayEntry]
    september: list[DayEntry]
    october: list[DayEntry]
    november: list[DayEntry]
    december: list[DayEntry]


class MemoryDetailData(BaseModel):
    memory_date: Date
    note: str
    mood: Mood
    rating: int
    img_url: str


class MemoryDetailResponse(BaseModel):
    before: list[DayEntry]
    after: list[DayEntry]
    data: MemoryDetailData | None = None