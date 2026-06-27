from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session
from src.auth.models import RefreshToken
from src.auth.schemas import ChangePasswordRequest, LoginRequest, Token
from src.auth import repository
from src.core.config import get_settings
from src.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from src.users.models import User
from src.users.repository import create, get_by_id, get_by_username, update
from src.users.schemas import UserCreate

settings = get_settings()


def register(db: Session, user_create: UserCreate) -> User:
    if get_by_username(db, user_create.username):
        raise UserAlreadyExistsError()

    user = User(
        username=user_create.username,
        hashed_password=hash_password(user_create.password)
    )

    return create(db, user)


def login(db: Session, data: LoginRequest) -> tuple[Token, RefreshToken]:
    user = get_by_username(db, data.username)

    if user is None:
        raise InvalidCredentialsError()

    if not verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = create_access_token(subject=str(user.id))

    token = create_refresh_token()
    refresh_token = RefreshToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    repository.create(db, refresh_token)

    return Token(access_token=access_token), refresh_token


def refresh_tokens(db: Session, refresh_token_value: str) -> tuple[Token, RefreshToken]:
    stored_token = repository.get_by_token(db, refresh_token_value)

    if stored_token is None:
        raise InvalidCredentialsError()

    if stored_token.expires_at < datetime.now(UTC):
        repository.revoke(db, stored_token)
        raise InvalidCredentialsError()

    repository.revoke(db, stored_token)

    access_token = create_access_token(subject=str(stored_token.user_id))

    new_token_value = create_refresh_token()
    new_refresh_token = RefreshToken(
        user_id=stored_token.user_id,
        token=new_token_value,
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    repository.create(db, new_refresh_token)

    return Token(access_token=access_token), new_refresh_token


def logout(db: Session, refresh_token_value: str) -> None:
    stored_token = repository.get_by_token(db, refresh_token_value)
    if stored_token:
        repository.revoke(db, stored_token)


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:

    if not verify_password(data.current_password, user.hashed_password):
        raise InvalidCredentialsError()

    user.hashed_password = hash_password(data.new_password)
    update(db, user)

    repository.revoke_all_for_user(db, user.id)
