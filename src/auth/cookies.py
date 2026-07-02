from fastapi import Request, Response
from src.core.config import get_settings

settings = get_settings()


def get_refresh_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.COOKIE_MAX_AGE,
        path=settings.COOKIE_PATH,
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path=settings.COOKIE_PATH,
    )
