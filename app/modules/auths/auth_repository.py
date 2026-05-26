from datetime import datetime, timezone
from sqlmodel import Session, select

from app.modules.auths.refresh_token_model import RefreshToken
from app.modules.users.user_model import User


class AuthRepository:

    def __init__(self, db: Session):
        self.db = db

    # USER

    def get_user_by_id(self, user_id: str) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.db.exec(statement).first()

    def create_user(
        self,
        google_id: str,
        email: str,
        username: str,
        profile_url: str,
    ) -> User:
        user = User(
            id=google_id,
            email=email,
            username=username,
            profile_url=profile_url,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create_user(
        self,
        google_id: str,
        email: str,
        username: str,
        profile_url: str,
    ) -> User:
        user = self.get_user_by_id(google_id)
        if not user:
            user = self.create_user(google_id, email, username, profile_url)
        return user

    # REFRESH TOKEN

    def get_refresh_token(self, token: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token == token)
        return self.db.exec(statement).first()

    def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(db_token)
        self.db.commit()
        return db_token

    def delete_refresh_token(self, db_token: RefreshToken) -> None:
        self.db.delete(db_token)
        self.db.commit()

    def validate_refresh_token(self, token: str) -> RefreshToken | None:
        db_token = self.get_refresh_token(token)
        if not db_token:
            return None
        expiers_at = db_token.expires_at.replace(tzinfo=timezone.utc)
        if expiers_at < datetime.now(timezone.utc):
            self.delete_refresh_token(db_token)
            return None
        return db_token
