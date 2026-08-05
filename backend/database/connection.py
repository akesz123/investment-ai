from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import settings
from backend.database.base import Base


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all database tables.

    In a production deployment you may prefer Alembic migrations, but for this
    project we ensure the schema exists at startup.
    """

    Base.metadata.create_all(bind=engine)
