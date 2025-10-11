from sqlmodel import SQLModel, Session, create_engine

from app.config import settings
from app.models import User

engine = create_engine(settings.database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
