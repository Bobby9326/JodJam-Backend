from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.users.user_model import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.db.exec(statement).first()

    def update_user(
        self,
        user: User,
        username: str | None = None,
        profile_url: str | None = None,
        bio: str | None = None,
    ) -> User:
        if username is not None:
            user.username = username
        if profile_url is not None:
            user.profile_url = profile_url
        if bio is not None:
            user.bio = bio

        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Username already taken")

        self.db.refresh(user)
        return user