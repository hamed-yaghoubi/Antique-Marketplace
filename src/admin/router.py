from fastapi import APIRouter, HTTPException, status
from src.users import service
from src.users.schemas import UserResponse
from src.core.exceptions import ProductNotFoundError, UserNotFoundError
from src.dependencies.auth import CurrentAdmin
from src.dependencies.db import DbSession
from src.products import service as products_service
from src.users.role import UserRole
from src.users import repository as users_repository

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


@router.patch("/users/{user_id}/ban", response_model=UserResponse)
def ban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.ban_user(db, user_id, current_admin)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch("/users/{user_id}/unban", response_model=UserResponse)
def unban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        return service.unban_user(db, user_id, current_admin)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DbSession, current_admin: CurrentAdmin):
    try:
        product = products_service.get_product(db, product_id)
        seller = users_repository.get_by_id(db, product.seller_id)
        if current_admin.role == UserRole.ADMIN and seller and seller.role in (UserRole.ADMIN, UserRole.OWNER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot delete products belonging to admins or owners"
            )
        products_service.repository.delete(db, product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)