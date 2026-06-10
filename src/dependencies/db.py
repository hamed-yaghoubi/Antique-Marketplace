from src.db.session import SessionLocal
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    with SessionLocal() as session:
        yield session

DbSession = Annotated[Session, Depends(get_db)]