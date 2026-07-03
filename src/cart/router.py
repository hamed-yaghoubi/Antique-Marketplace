from fastapi import APIRouter, status
from src.cart.schemas import CartItemCreate, CartItemUpdate, CartResponse
from src.cart import service
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
def read_cart(db: DbSession, current_user: CurrentUser):
    return service.get_cart(db, current_user)

@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(data: CartItemCreate, db: DbSession, current_user: CurrentUser):
    return service.add_item(db, data, current_user)

@router.patch("/items/{item_id}")
def update_cart_item(item_id: int, data: CartItemUpdate, db: DbSession, current_user: CurrentUser):
    return service.update_item_quantity(db, item_id, data, current_user)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(item_id: int, db: DbSession, current_user: CurrentUser):
    service.remove_item(db, item_id, current_user)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(db: DbSession, current_user: CurrentUser):
    service.clear_cart(db, current_user)
