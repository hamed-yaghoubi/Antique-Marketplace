from sqlalchemy import select
from sqlalchemy.orm import Session
from src.users.models import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_by_username(db: Session, username: str) -> User | None:
    query = select(User).where(User.username == username)

    return db.execute(query).scalar_one_or_none()

def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def update(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    
    return user

def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()