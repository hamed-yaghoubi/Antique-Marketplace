from sqlalchemy.orm import Session
import jwt
from src.auth.schemas import ChangePasswordRequest, LoginRequest, TokenResponse
from src.core import security
from src.core.config import get_settings
from src.core.exceptions import InvalidCredentialsError
from src.users.models import User
from src.users import repository

settings = get_settings()


def register(db: Session, user_create) -> User:
    if repository.get_by_username(db, user_create.username):
        from src.core.exceptions import UserAlreadyExistsError
        raise UserAlreadyExistsError()

    user = User(
        username=user_create.username,
        hashed_password=security.hash_password(user_create.password)
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


def refresh_tokens(refresh_token_value: str) -> TokenResponse:
    try:
        payload = security.decode_refresh_token(refresh_token_value)
        user_id = payload["sub"]
    except jwt.InvalidTokenError:
        raise InvalidCredentialsError()

    access_token = security.create_access_token(subject=user_id)
    refresh_token = security.create_refresh_token(subject=user_id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def logout() -> None:
    pass  # Stateless tokens - client deletes cookie


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:
    if not security.verify_password(data.current_password, user.hashed_password):
        raise InvalidCredentialsError()

    user.hashed_password = security.hash_password(data.new_password)
    repository.update(db, user)
