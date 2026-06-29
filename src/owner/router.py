from fastapi import APIRouter, HTTPException, status
from src.dependencies.auth import CurrentOwner
from src.dependencies.db import DbSession
from src.users import repository as users_repository
from src.users.models import User
from src.users.role import UserRole
from src.products import service as products_service
from src.admin.schemas import UserResponse

router = APIRouter(prefix="/owner", tags=["Owner"])


@router.post("/promote/{user_id}", response_model=UserResponse)
def promote_to_admin(user_id: int, db: DbSession, current_owner: CurrentOwner):
    user = users_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_owner.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    if user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change role of another owner"
        )

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )

    user.role = UserRole.ADMIN
    users_repository.update(db, user)
    return user


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_product(product_id: int, db: DbSession, current_owner: CurrentOwner):
    try:
        product = products_service.get_product(db, product_id)
        products_service.repository.delete(db, product)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
