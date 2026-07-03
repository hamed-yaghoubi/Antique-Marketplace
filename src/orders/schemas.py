from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from src.orders.orderstatus import OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_title: str
    unit_price: Decimal
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderCard(BaseModel):
    id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    buyer_id: int | None = None
    buyer_username: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_order(cls, order) -> "OrderCard":
        buyer = getattr(order, "buyer", None)
        return cls(
            id=order.id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at,
            buyer_id=order.buyer_id,
            buyer_username=getattr(buyer, "username", None) if buyer else None,
        )


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class OrderFilter(BaseModel):
    search: str | None = None
    status: OrderStatus | None = None
    seller_id: int | None = None
    buyer_id: int | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class PaginatedOrderResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class OrderStats(BaseModel):
    total: int = 0
    pending: int = 0
    confirmed: int = 0
    preparing: int = 0
    shipped: int = 0
    delivered: int = 0
    cancelled: int = 0


class DashboardStats(BaseModel):
    order_stats: OrderStats
    total_products: int = 0
    active_products: int = 0
    total_users: int = 0
    total_revenue: Decimal = Decimal("0.00")

