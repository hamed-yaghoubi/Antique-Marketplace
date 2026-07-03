from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings

settings = get_settings()

_is_sqlite = settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,
}

if not _is_sqlite:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine)