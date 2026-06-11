from fastapi import APIRouter, HTTPException, status
from src.core.exceptions import InsufficientStockError, OrderNotFoundError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.orders.schemas import OrderCard, OrderResponse, OrderStatusUpdate
from src.orders import service

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_new_order(db: DbSession, current_user: CurrentUser):
    try:
        return service.create_order(db, current_user)

    except InsufficientStockError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.get("/", response_model=list[OrderCard])
def read_orders(db: DbSession, current_user: CurrentUser):
    return service.get_orders(db, current_user)

@router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: DbSession, current_user: CurrentUser):
    try:
        return service.get_order(db, order_id, current_user)

    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

@router.patch("/{order_id}/status", response_model=OrderResponse)
def patch_order_status(order_id: int, data: OrderStatusUpdate, db: DbSession):
    try:
        return service.update_order_status(db, order_id, data)

    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)