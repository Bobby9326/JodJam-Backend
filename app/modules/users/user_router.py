from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import APIKeyCookie
from sqlmodel import Session

import jwt

from app.core.config import settings
from app.core.database import get_session
from app.core.dependencies import get_current_user_id
from app.modules.users.user_repository import UserRepository
from app.modules.users.user_service import UserService
from app.modules.users.user_schema import (
    MeResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
    UploadAvatarResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# --- Dependency ---

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)




# --- Endpoints ---

@router.get("/me", response_model=MeResponse)
def get_me(
    user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
):
    try:
        return service.get_me(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/me", response_model=UpdateProfileResponse)
def update_me(
    body: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
):
    # ป้องกัน request เปล่า
    if body.username is None and body.profile_url is None and body.bio is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        return service.update_profile(
            user_id=user_id,
            username=body.username,
            profile_url=body.profile_url,
            bio=body.bio,
        )
    except ValueError as e:
        err = str(e)
        if "already taken" in err:
            raise HTTPException(status_code=409, detail=err)
        raise HTTPException(status_code=404, detail=err)


@router.post("/me/avatar", response_model=UploadAvatarResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
):
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_IMAGE_TYPES}",
        )

    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    try:
        return service.upload_avatar(
            user_id=user_id,
            file_bytes=file_bytes,
            content_type=file.content_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))