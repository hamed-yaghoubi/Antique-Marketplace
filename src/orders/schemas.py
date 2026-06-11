from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

