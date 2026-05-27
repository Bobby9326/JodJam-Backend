import calendar
from datetime import date as Date, timedelta

from app.core.supabase_storage import generate_signed_url, upload_memory_image
from app.modules.memories.memory_model import Memory, Mood
from app.modules.memories.memory_repository import MemoryRepository
from app.modules.memories.memory_schema import (
    CalendarResponse,
    CreateMemoryResponse,
    DayEntry,
    MemoryDetailData,
    MemoryDetailResponse,
)

MONTH_NAMES = [
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december",
]


def _resolve_image_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    return generate_signed_url(image_path)


def _to_day_entry(date: Date, memory: Memory | None) -> DayEntry:
    if memory:
        return DayEntry(
            date=date,
            has_entry=True,
            img_url=_resolve_image_url(memory.image_path),
        )
    return DayEntry(date=date, has_entry=False, img_url=None)


class MemoryService:

    def __init__(self, repo: MemoryRepository):
        self.repo = repo

    # --- CREATE ---

    def create_memory(
        self,
        user_id: str,
        memory_date: Date,
        file_bytes: bytes,
        content_type: str,
        note: str,
        mood: Mood,
        rating: int,
    ) -> CreateMemoryResponse:
        # Upload image first; path = entries/memories/{user_id}/{date}
        image_path = upload_memory_image(user_id, str(memory_date), file_bytes, content_type)

        memory = self.repo.create_memory(
            user_id=user_id,
            memory_date=memory_date,
            image_path=image_path,
            note=note,
            mood=mood,
            rating=rating,
        )

        return CreateMemoryResponse(
            id=str(memory.id),
            memory_date=memory.memory_date,
            image_path=memory.image_path,
            note=memory.note,
            mood=memory.mood,
            rating=memory.rating,
        )

    # --- CALENDAR ---

    def get_calendar(self, user_id: str, year: int) -> CalendarResponse:
        memories = self.repo.get_by_year(user_id, year)
        # Build lookup: date → Memory
        memory_map: dict[Date, Memory] = {m.memory_date: m for m in memories}

        months: dict[str, list[DayEntry]] = {}

        for month_idx, month_name in enumerate(MONTH_NAMES, start=1):
            _, days_in_month = calendar.monthrange(year, month_idx)
            entries: list[DayEntry] = []
            for day in range(1, days_in_month + 1):
                d = Date(year, month_idx, day)
                entries.append(_to_day_entry(d, memory_map.get(d)))
            months[month_name] = entries

        return CalendarResponse(**months)

    # --- DETAIL ---

    def get_memory_detail(self, user_id: str, target_date: Date) -> MemoryDetailResponse:
        # Fetch 7-day window: 3 before, target, 3 after
        start = target_date - timedelta(days=3)
        end = target_date + timedelta(days=3)
        memories = self.repo.get_range(user_id, start, end)
        memory_map: dict[Date, Memory] = {m.memory_date: m for m in memories}

        before = [
            _to_day_entry(target_date - timedelta(days=i), memory_map.get(target_date - timedelta(days=i)))
            for i in range(3, 0, -1)   # 3 days before, chronological order
        ]

        after = [
            _to_day_entry(target_date + timedelta(days=i), memory_map.get(target_date + timedelta(days=i)))
            for i in range(1, 4)        # 3 days after
        ]

        target_memory = memory_map.get(target_date)
        data = None
        if target_memory:
            data = MemoryDetailData(
                memory_date=target_memory.memory_date,
                note=target_memory.note,
                mood=target_memory.mood,
                rating=target_memory.rating,
            )

        return MemoryDetailResponse(before=before, after=after, data=data)