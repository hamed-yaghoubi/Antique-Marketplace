from sqlalchemy.orm import Session
from fastapi import HTTPException, status
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


def update_user_role(db: Session, user_id: int, role: UserRole, current_user: User) -> User:
    target = get_user(db, user_id)

    if target.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    if current_user.role == UserRole.ADMIN:
        if target.role in (UserRole.ADMIN, UserRole.OWNER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot change role of other admins or owners"
            )
        if role != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only assign the user role"
            )

    target.role = role
    return repository.update(db, target)


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
