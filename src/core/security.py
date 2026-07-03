from datetime import UTC, datetime, timedelta
from typing import Any
import jwt
from pwdlib import PasswordHash
from src.core.config import get_settings

settings = get_settings()

password_hash = PasswordHash.recommended()

# Use different keys for access and refresh tokens for better security
_ACCESS_TOKEN_KEY = settings.SECRET_KEY + "_access"
_REFRESH_TOKEN_KEY = settings.SECRET_KEY + "_refresh"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(UTC) + expires_delta

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        payload,
        _ACCESS_TOKEN_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            _ACCESS_TOKEN_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")

    return payload


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        _REFRESH_TOKEN_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_refresh_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            _REFRESH_TOKEN_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Refresh token expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Invalid token type")

    return payload
