
from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.security import APIKeyCookie
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session

from app.modules.memories.memory_repository import MemoryRepository
from app.modules.stats.stat_schema import OverviewResponse, MoodStatsResponse , YearlyMoodStatsResponse , YearlyRatingStatsResponse
from app.core.dependencies import get_current_user_id
from app.modules.stats.stat_service import StatService


router = APIRouter(prefix="/stats", tags=["stats"])

def get_memory_service(session: Session = Depends(get_session)) -> StatService:
    repo = MemoryRepository(session)
    return StatService(repo)


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    year: int = Query(..., ge=2000, le=2100, description="ปีที่ต้องการดึงข้อมูล"),
    user_id: str = Depends(get_current_user_id),
    service: StatService = Depends(get_memory_service),
):
    return service.get_overview(user_id, year)

@router.get("/mood", response_model=MoodStatsResponse)
def get_mood_stats(
    year: int = Query(..., ge=2000, le=2100, description="ปีที่ต้องการดึงข้อมูล"),
    user_id: str = Depends(get_current_user_id),
    service: StatService = Depends(get_memory_service),
):
    return service.get_mood_stats(user_id, year)

@router.get("/yearly-average", response_model=YearlyRatingStatsResponse)
def get_yearly_rating_stats(
    year: int = Query(..., ge=2000, le=2100, description="ปีที่ต้องการดึงข้อมูล"),
    user_id: str = Depends(get_current_user_id),
    service: StatService = Depends(get_memory_service),
):
    return service.get_yearly_rating_stats(user_id, year)

@router.get("/yearly-mood", response_model=YearlyMoodStatsResponse)
def get_yearly_mood_stats(
    year: int = Query(..., ge=2000, le=2100, description="ปีที่ต้องการดึงข้อมูล"),
    user_id: str = Depends(get_current_user_id),
    service: StatService = Depends(get_memory_service),
):
    return service.get_yearly_mood_stats(user_id, year)
