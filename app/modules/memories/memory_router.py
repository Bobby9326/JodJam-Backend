from datetime import date as Date

from fastapi.params import Depends, File, Query
import jwt
from fastapi import APIRouter,  HTTPException, UploadFile
from fastapi.security import APIKeyCookie
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.dependencies import get_current_user_id
from app.modules.memories.memory_model import Mood
from app.modules.memories.memory_repository import MemoryRepository
from app.modules.memories.memory_service import MemoryService
from app.modules.memories.memory_schema import (
    CreateMemoryResponse,
    CalendarResponse,
    MemoryDetailResponse,
)

router = APIRouter(prefix="/memories", tags=["memories"])


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# --- Dependencies ---

def get_memory_service(session: Session = Depends(get_session)) -> MemoryService:
    repo = MemoryRepository(session)
    return MemoryService(repo)




# --- POST /memories ---

@router.post("", response_model=CreateMemoryResponse, status_code=201)
async def create_memory(
    note: str,
    mood: Mood,
    rating: int,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: jpeg, png, webp",
        )

    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    memory_date = Date.today()  # Use current date for memory entry; can be changed to accept from client if needed

    try:
        return service.create_memory(
            user_id=user_id,
            memory_date=memory_date,
            file_bytes=file_bytes,
            content_type=file.content_type,
            note=note,
            mood=mood,
            rating=rating,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- GET /memories/calendar ---

@router.get("/calendar", response_model=CalendarResponse)
def get_calendar(
    year: int = Query(..., ge=2000, le=2100, description="ปีที่ต้องการดึงข้อมูล"),
    user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
):
    return service.get_calendar(user_id, year)


# --- GET /memories/{date} ---

@router.get("/{date}", response_model=MemoryDetailResponse)
def get_memory_detail(
    date: Date,
    user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
):
    return service.get_memory_detail(user_id, date)