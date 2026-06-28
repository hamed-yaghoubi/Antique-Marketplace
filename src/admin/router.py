from fastapi import APIRouter, HTTPException, status
from src.admin import service
from src.admin.schemas import UserResponse, UserUpdateRole, UserBan
from src.core.exceptions import ProductNotFoundError, UserNotFoundError
from src.dependencies.auth import CurrentAdmin
from src.dependencies.db import DbSession
from src.products import service as products_service
from src.products.schemas import ProductResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: DbSession, current_admin: CurrentAdmin):
    return service.get_all_users(db)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.get_user(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: int, data: UserUpdateRole, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.update_user_role(db, user_id, data.role)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch("/users/{user_id}/ban", response_model=UserResponse)
def ban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.ban_user(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch("/users/{user_id}/unban", response_model=UserResponse)
def unban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.unban_user(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        product = products_service.get_product(db, product_id)
        products_service.repository.delete(db, product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
