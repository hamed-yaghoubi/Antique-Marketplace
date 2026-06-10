from sqlalchemy.orm import Session
from src.auth.schemas import ChangePasswordRequest, LoginRequest, Token
from src.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.core.security import hash_password, verify_password, create_access_token
from src.users.models import User
from src.users.repository import create, get_by_username, update
from src.users.schemas import UserCreate


def register(db: Session, user_create: UserCreate) -> User:
    if get_by_username(db, user_create.username):
        raise UserAlreadyExistsError()

    user = User(
        username=user_create.username,
        hashed_password=hash_password(user_create.password)
    )

    return create(db, user)


def login(db: Session, data: LoginRequest) -> Token:
    user = get_by_username(db, data.username)

    if user is None:
        raise InvalidCredentialsError()

    if not verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = create_access_token(subject=str(user.id))

    return Token(access_token=access_token)


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:

    if not verify_password(data.current_password, user.hashed_password):
        raise InvalidCredentialsError()

    user.hashed_password = hash_password(data.new_password)

    update(db, user)