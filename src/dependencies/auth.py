from typing import Annotated
from jwt import InvalidTokenError
from src.core.exceptions import InvalidCredentialsError
from src.core.security import decode_access_token
from src.dependencies.db import DbSession
from src.users.models import User
from src.users.repository import get_by_id
from fastapi import Cookie, Depends, Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_access_token(request: Request, token: str | None = Depends(oauth2_scheme)) -> str:
    if token:
        return token

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    raise InvalidCredentialsError()


def get_current_user(db: DbSession, token: str = Depends(get_access_token)) -> User:
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
