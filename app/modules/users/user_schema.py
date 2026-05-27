from sqlite3 import Date

from pydantic import BaseModel


class MeResponse(BaseModel):
    id: str
    email: str
    username: str
    profile_url: str | None = None
    bio: str | None = None
    first_date: Date
    amount_of_memories: int
    number_of_days_joined: int


class UpdateProfileRequest(BaseModel):
    username: str | None = None
    profile_url: str | None = None
    bio: str | None = None


class UpdateProfileResponse(BaseModel):
    id: str
    email: str
    username: str
    profile_url: str | None = None
    bio: str | None = None


class UploadAvatarResponse(BaseModel):
    path: str  # storage path, e.g. "profile/abc123"

    