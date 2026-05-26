from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    picture: str | None = None


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


class TokenRefreshResponse(BaseModel):
    message: str


class LogoutResponse(BaseModel):
    message: str


class MeResponse(BaseModel):
    id: str
    email: str
    username: str
