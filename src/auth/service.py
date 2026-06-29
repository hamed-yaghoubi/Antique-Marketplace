from sqlalchemy.orm import Session
from sqlalchemy import func
import jwt
from fastapi import HTTPException, status
from src.auth.schemas import ChangePasswordRequest, LoginRequest, TokenResponse
from src.core import security
from src.core.config import get_settings
from src.core.exceptions import InvalidCredentialsError
from src.users.models import User
from src.users.role import UserRole
from src.users import repository

settings = get_settings()


def register(db: Session, user_create) -> User:
    if repository.get_by_username(db, user_create.username):
        from src.core.exceptions import UserAlreadyExistsError
        raise UserAlreadyExistsError()

    user_count = db.query(func.count()).select_from(User).scalar()
    role = UserRole.OWNER if user_count == 0 else UserRole.USER

    user = User(
        username=user_create.username,
        hashed_password=security.hash_password(user_create.password),
        role=role,
    )

    return repository.create(db, user)


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = repository.get_by_username(db, data.username)

    if user is None:
        raise InvalidCredentialsError()

    if not security.verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def refresh_tokens(db: Session, refresh_token_value: str) -> TokenResponse:
    try:
        payload = security.decode_refresh_token(refresh_token_value)
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = security.create_access_token(subject=str(user_id))
    refresh_token = security.create_refresh_token(subject=str(user_id))

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def logout() -> None:
    pass  # Stateless tokens - client deletes cookie


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:
    if not security.verify_password(data.current_password, user.hashed_password):
        raise InvalidCredentialsError()

    user.hashed_password = security.hash_password(data.new_password)
    repository.update(db, user)
