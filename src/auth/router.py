from fastapi import APIRouter, HTTPException, Response, status, Depends, Request
from src.auth.schemas import LoginRequest, TokenResponse, ChangePasswordRequest
from src.auth import service
from src.core.config import get_settings
from src.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.users.schemas import UserCreate, UserResponse

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])


def get_refresh_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)


def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.COOKIE_MAX_AGE,
        path=settings.COOKIE_PATH,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: DbSession):
    try:
        return service.register(db, user_create)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: DbSession, response: Response):
    try:
        tokens = service.login(db, data)
        set_refresh_cookie(response, tokens.refresh_token)
        return tokens
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    response: Response,
    refresh_token_value: str | None = Depends(get_refresh_token_from_cookie),
):
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")

    try:
        tokens = service.refresh_tokens(refresh_token_value)
        set_refresh_cookie(response, tokens.refresh_token)
        return tokens
    except InvalidCredentialsError:
        response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path=settings.COOKIE_PATH)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(response: Response):
    response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path=settings.COOKIE_PATH)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/change-password")
def update_password(
    data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession
):
    try:
        service.change_password(db, current_user, data)
        return {"message": "Password changed successfully"}
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
