from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.core.exceptions import UserNotFoundError
from src.users.models import User
from src.users import repository
from src.users.schemas import UserUpdate
from src.users.role import UserRole

def get_user(db: Session, user_id: int) -> User:
    user = repository.get_by_id(db, user_id)

    if user is None:
        raise UserNotFoundError()

    return user

def get_user_by_username(db: Session, username: str) -> User:
    user = repository.get_by_username(db, username)

    if user is None:
        raise UserNotFoundError()

    return user

def update_user(db: Session, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    return repository.update(db, user)

def delete_user(db: Session, user: User) -> None:
    repository.delete(db, user)

def get_all_users(db: Session) -> list[User]:
    return repository.get_all_users(db)

def ban_user(db: Session, user_id: int, current_user: User) -> User:
    target = get_user(db, user_id)

    if target.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban yourself"
        )

    if current_user.role == UserRole.ADMIN and target.role in (UserRole.ADMIN, UserRole.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot ban other admins or owners"
        )

    target.is_active = False
    return repository.update(db, target)

def unban_user(db: Session, user_id: int, current_user: User) -> User:
    target = get_user(db, user_id)

    if current_user.role == UserRole.ADMIN and target.role in (UserRole.ADMIN, UserRole.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot unban other admins or owners"
        )

    target.is_active = True
    return repository.update(db, target)