from typing import Annotated
from jwt import InvalidTokenError
from src.core.exceptions import InvalidCredentialsError
from src.core.security import decode_access_token
from src.dependencies.db import DbSession
from src.users.models import User
from src.users.repository import get_by_id
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(db: DbSession, token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_access_token(token)

        user_id = int(payload["sub"])

    except (InvalidTokenError, KeyError, ValueError):
        raise InvalidCredentialsError()

    user = get_by_id(db, user_id)

    if user is None:
        raise InvalidCredentialsError()

    return user


CurrentUser = Annotated[User,Depends(get_current_user)]