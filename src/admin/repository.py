from sqlalchemy import select
from sqlalchemy.orm import Session
from src.users.models import User


def get_all_users(db: Session) -> list[User]:
    query = select(User)
    return list(db.execute(query).scalars().all())


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def update(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    return user
