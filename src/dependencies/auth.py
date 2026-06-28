from typing import Annotated
from jwt import InvalidTokenError
from src.core import security
from src.core.exceptions import InvalidCredentialsError
from src.dependencies.db import DbSession
from src.users import repository
from src.users.models import User
from src.users.role import UserRole
from fastapi import Depends, HTTPException, Request, status
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
        payload = security.decode_access_token(token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise InvalidCredentialsError()

    user = repository.get_by_id(db, user_id)

    if user is None:
        raise InvalidCredentialsError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
