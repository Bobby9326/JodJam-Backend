from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.core.config import settings
from app.modules.auths.refresh_token_model import RefreshToken
from app.modules.users.user_model import User
from app.modules.auths.auth_repository import AuthRepository

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM


class AuthService:

    def __init__(self, repo: AuthRepository):
        self.repo = repo

    # TOKENS

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def create_refresh_token(self) -> str:
        return str(uuid4())

    def decode_access_token(self, token: str) -> dict:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # GOOGLE LOGIN

    def handle_google_login(self, user_info: dict) -> tuple[User, str, str]:
        """
        Upsert user from Google userinfo, issue tokens.
        Returns (user, access_token, refresh_token).
        """
        google_id = user_info.get("sub")
        email = user_info.get("email")
        username = user_info.get("name")
        picture = user_info.get("picture")

        user = self.repo.get_or_create_user(
            google_id=google_id,
            email=email,
            username=username,
            profile_url=picture,
        )

        access_token = self.create_access_token({
            "sub": user.id,
            "email": user.email,
            "username": user.username,
        })

        refresh_token = self.create_refresh_token()
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self.repo.create_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expires,
        )

        return user, access_token, refresh_token

    # REFRESH

    def handle_refresh(self, refresh_token: str) -> str:
        """
        Validate refresh token, issue new access token.
        Returns new access_token string.
        Raises ValueError on invalid/expired token.
        """
        db_token = self.repo.validate_refresh_token(refresh_token)
        if not db_token:
            raise ValueError("Invalid or expired refresh token")

        user = self.repo.get_user_by_id(db_token.user_id)
        if not user:
            raise ValueError("User not found")

        return self.create_access_token({
            "sub": user.id,
            "email": user.email,
            "username": user.username,
        })

    # LOGOUT

    def handle_logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        db_token = self.repo.get_refresh_token(refresh_token)
        if db_token:
            self.repo.delete_refresh_token(db_token)
