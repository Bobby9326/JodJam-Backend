from sqlmodel import SQLModel, create_engine, Session
from app.modules.memories.memory_model import Memory
from app.modules.users.user_model import User
from app.modules.auths.refresh_token_model import RefreshToken
from app.core.config import settings

db_host = settings.DATABASE_URL
engine = create_engine(db_host, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session