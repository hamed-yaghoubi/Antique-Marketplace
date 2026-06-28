from sqlalchemy.orm import Session
from src.admin import repository
from src.core.exceptions import UserNotFoundError
from src.users.models import User
from src.users.role import UserRole


def get_all_users(db: Session) -> list[User]:
    return repository.get_all_users(db)


def get_user(db: Session, user_id: int) -> User:
    user = repository.get_by_id(db, user_id)
    if user is None:
        raise UserNotFoundError()
    return user


def update_user_role(db: Session, user_id: int, role: UserRole) -> User:
    user = get_user(db, user_id)
    user.role = role
    return repository.update(db, user)


def ban_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.is_active = False
    return repository.update(db, user)


def unban_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.is_active = True
    return repository.update(db, user)
