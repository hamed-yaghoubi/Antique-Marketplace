from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.orders.orderstatus import OrderStatus
from src.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)

    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    buyer: Mapped["User"] = relationship("User", back_populates="orders")

    items: Mapped[list[OrderItem]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")



class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    product_title: Mapped[str] = mapped_column(String(255))

    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    quantity: Mapped[int]

    order: Mapped[Order] = relationship("Order", back_populates="items")