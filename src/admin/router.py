from fastapi import APIRouter, Query, status
from src.users import service
from src.users.schemas import UserResponse
from src.dependencies.auth import CurrentAdmin
from src.dependencies.db import DbSession
from src.products import service as products_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: DbSession,
    current_admin: CurrentAdmin,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return service.get_all_users(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    return service.get_user(db, user_id)


@router.patch("/users/{user_id}/ban", response_model=UserResponse)
def ban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    return service.ban_user(db, user_id, current_admin)


@router.patch("/users/{user_id}/unban", response_model=UserResponse)
def unban_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    return service.unban_user(db, user_id, current_admin)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DbSession, current_admin: CurrentAdmin):
    products_service.admin_delete_product(db, product_id, current_admin)
