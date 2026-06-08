from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)