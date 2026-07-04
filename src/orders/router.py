import math
from datetime import datetime
from fastapi import APIRouter, Query, status
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.orders.orderstatus import OrderStatus
from src.orders.schemas import (
    OrderCard,
    OrderFilter,
    OrderResponse,
    OrderStats,
    OrderStatusUpdate,
    PaginatedOrderResponse,
    PaginationParams,
)
from src.orders import service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/stats", response_model=OrderStats)
def read_order_stats(db: DbSession, current_user: CurrentUser):
    return service.get_order_stats(db, current_user)


@router.get("/dashboard")
def read_dashboard_stats(db: DbSession, current_user: CurrentUser):
    return service.get_dashboard_stats(db, current_user)


@router.get("/", response_model=PaginatedOrderResponse)
def read_orders(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    status: OrderStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = Query(default=None, alias="date_from"),
    date_to: datetime | None = Query(default=None, alias="date_to"),
    seller_id: int | None = Query(default=None, alias="seller_id"),
    buyer_id: int | None = Query(default=None, alias="buyer_id"),
    view: str = Query(default="buyer", alias="view"),
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = OrderFilter(
        search=search,
        status=status,
        seller_id=seller_id,
        buyer_id=buyer_id,
        created_after=date_from,
        created_before=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    orders, total = service.get_filtered_orders(db, filters, pagination, current_user, view=view)
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 0

    return PaginatedOrderResponse(
        items=[OrderCard.from_order(o) for o in orders],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: DbSession, current_user: CurrentUser, view: str = Query(default="buyer")):
    return service.get_order(db, order_id, current_user, view=view)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_new_order(db: DbSession, current_user: CurrentUser):
    return service.create_order(db, current_user)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, data: OrderStatusUpdate, db: DbSession, current_user: CurrentUser):
    return service.update_order_status(db, order_id, data, current_user)
