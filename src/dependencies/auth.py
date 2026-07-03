from typing import Annotated
import jwt
from src.core import security
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BannedAccountError,
    InvalidTokenError,
    TokenExpiredError,
    UserNotFoundError,
)
from src.dependencies.db import DbSession
from src.users import repository
from src.users.models import User
from src.users.role import UserRole
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_access_token(request: Request, token: str | None = Depends(oauth2_scheme)) -> str:
    if token:
        return token

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    raise AuthenticationError("Not authenticated")


def get_current_user(db: DbSession, token: str = Depends(get_access_token)) -> User:
    try:
        payload = security.decode_access_token(token)
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise InvalidTokenError()

    user = repository.get_by_id(db, user_id)

    if user is None:
        raise UserNotFoundError()

    if not user.is_active:
        raise BannedAccountError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.OWNER):
        raise AuthorizationError("Admin access required")
    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]


def get_current_owner(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.OWNER:
        raise AuthorizationError("Owner access required")
    return current_user


CurrentOwner = Annotated[User, Depends(get_current_owner)]
