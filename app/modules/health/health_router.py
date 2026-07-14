from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from app.core.database import get_session

router = APIRouter(prefix="/health",tags=["Health"])


@router.api_route("", methods=["GET", "HEAD"])
async def health():
    return {
        "status": "ok",
        "service": "JodJam API",
        "version": "1.0.0",
    }


@router.api_route("/db", methods=["GET", "HEAD"])
async def health_db(db: Session = Depends(get_session)):
    try:
        db.exec(text("SELECT 1"))
        return {
            "status": "ok",
            "service": "JodJam API",
            "db": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "JodJam API",
            "db": "disconnected",
            "detail": str(e),
        }