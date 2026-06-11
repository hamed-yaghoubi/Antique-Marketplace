from fastapi import APIRouter, HTTPException, status
from src.auth.schemas import LoginRequest, Token, ChangePasswordRequest
from src.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.users.schemas import UserCreate, UserResponse
from src.auth.service import register, login, change_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: DbSession):
    try:
        return register(db, user_create)

    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=Token)
def login_user(data: LoginRequest, db: DbSession):
    try:
        return login(db, data)

    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/change-password")
def update_password(data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession):
    try:
        change_password(db, current_user, data)

        return {
            "message": "Password changed successfully"
        }

    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)