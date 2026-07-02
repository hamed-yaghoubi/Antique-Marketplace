from fastapi import APIRouter, Response, status, Depends, Request
from src.auth.schemas import LoginRequest, TokenResponse, ChangePasswordRequest
from src.auth import service
from src.auth.cookies import get_refresh_token_from_cookie, set_refresh_cookie, delete_refresh_cookie
from src.core.exceptions import AppException, AuthenticationError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.users.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: DbSession):
    return service.register(db, user_create)


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: DbSession, response: Response):
    tokens = service.login(db, data)
    set_refresh_cookie(response, tokens.refresh_token)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    response: Response,
    db: DbSession,
    refresh_token_value: str | None = Depends(get_refresh_token_from_cookie),
):
    if not refresh_token_value:
        raise AuthenticationError("No refresh token provided")

    try:
        tokens = service.refresh_tokens(db, refresh_token_value)
        set_refresh_cookie(response, tokens.refresh_token)
        return tokens
    except AppException:
        delete_refresh_cookie(response)
        raise


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(response: Response):
    delete_refresh_cookie(response)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/change-password")
def update_password(
    data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession
):
    service.change_password(db, current_user, data)
    return {"message": "Password changed successfully"}
